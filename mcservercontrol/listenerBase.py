from abc import abstractmethod
from typing import Any, Callable, Dict, Literal, Tuple, TypedDict, List, Union
import os, warnings, signal
from multiprocessing import Process, Queue
from threading import Thread

from mcservercontrol import globalVar
from mcservercontrol.server import Server, MCPopen

from .configReader import config
from .player import Player
from .observer import PlayerObserver, PlayerCommandObserver, DaemonObserver
from .broadcastServer import startServer as startBroadcastServer

EVENT_TYPE = Literal[
    "general", 
    "login", 
    "logout",
    "speak",
    "cmd",
    "listplayer",
]


class EVENT_GENERAL(TypedDict):
    etype: EVENT_TYPE
    time: float                 # time stamp
    log_line: str               # original log

class EVENT_LOGIN(EVENT_GENERAL):
    player: Player

class EVENT_LOGOUT(EVENT_GENERAL):
    player: Player

class EVENT_CMD(EVENT_GENERAL):
    player: Player
    cmd_split: Tuple[str, List[str]]

class EVENT_SPEAK(EVENT_GENERAL):
    player: Player
    content: str

class EVENT_LISTPLAYER(EVENT_GENERAL):
    players: List[Player]

class EVENT_ALL(EVENT_GENERAL, total = False):
    # All possible entries, for type checking purpose
    players: List[Player]
    player: Player
    cmd_split: Tuple[str, List[str]]
    content: str


class InputThread(Thread):
    """
    Thread listening to user input from console
    """
    def __init__(self, mc_proc_getter: Callable[[], MCPopen]) -> None:
        """
         - mc_proc: minecraft server process
        """
        # daemon thread will end when main thread exit
        super().__init__(daemon=True)
        self._proc_getter = mc_proc_getter

    @property
    def mc_proc(self) -> MCPopen:
        return self._proc_getter()

    def run(self):
        while True:
            _usr_input = input()
            self.onInput(_usr_input)

    def onInput(self, x: str):
        self.sendServerCommand(x)

    def sendServerCommand(self, x: str):
        if not x.endswith("\n"):
            x += "\n"
        self.mc_proc.stdin.write(x.encode("utf-8"))
        self.mc_proc.stdin.flush()

class EventListenerBase:

    def __init__(self) -> None:
        self.players: Dict[str, Player] = {}
        self.player_observers: List[PlayerObserver] = []
        self.player_command_observers: Dict[str, PlayerCommandObserver] = {}
        self.event_queue = Queue()

        self.input_thread: InputThread
        self.daemon: DaemonObserver
    
    @property
    def mc_server(self):
        if globalVar.server:
            return globalVar.server
        else:
            raise Exception("uninitialized")
    
    def register(self, *obs: Union[PlayerObserver, PlayerCommandObserver]):
        for ob in obs:
            ob._all_players = self.players
            if isinstance(ob, PlayerObserver):
                self.player_observers.append(ob)
            if isinstance(ob, PlayerCommandObserver):
                self.player_command_observers[ob.entry] = ob
                
                # alias, same function, different name
                for al in ob.alias:
                    self.player_command_observers[al] = ob

    def addDaemonCallback(self, callback: Callable):
        self.daemon.addCallback(callback)

    def emit(self, event: EVENT_ALL):

        # print to console
        print(event["log_line"], end="")

        # send to broadcast server
        self.event_queue.put(event)

        if event["etype"] == "general":
            if event["log_line"].strip().endswith("[Server thread/INFO]: Saved the game"):
                self.mc_server.onWorldSaveCallback()

        if event["etype"] == "login":
            assert "player" in event
            # Load player status on login
            event["player"].loadStatus()

            for p_ob in self.player_observers:
                p_ob.onPlayerLogin(event["player"])

        if event["etype"] == "logout":
            assert "player" in event
            for p_ob in self.player_observers:
                p_ob.onPlayerLogout(event["player"])

            # Save player status on logout
            event["player"].saveStatus()

        if event["etype"] == "speak":
            assert "player" in event
            assert "content" in event
            for p_ob in self.player_observers:
                p_ob.onPlayerSpeak(event["player"], event["content"])

        if event["etype"] == "cmd":
            assert "player" in event
            assert "cmd_split" in event
            entry = event["cmd_split"][0]
            if entry in self.player_command_observers.keys():
                try:
                    self.player_command_observers[entry].onTriggered(
                        event["player"], event["cmd_split"][1]
                    )
                except Exception as e:
                    print("Error on command: {}".format(e))
            else:
                self.daemon.server.tellraw(
                    target = event["player"],
                    text = "Invalid command - {}".format(entry),
                    color = "red"
                )

    @property
    def cmd_interface(self) -> Callable[[str], Any]:
        if hasattr(self, "input_thread"):
            return self.input_thread.sendServerCommand
        else:
            return lambda x: warnings.warn("Minecraft command line interface not ready.")

    def startServer(self):
        os.chdir(config()["server_dir"])

        # A thread that listen to user input
        self.input_thread = InputThread(lambda: self.mc_server.proc)
        # Save server to global variable to be accessed by observers
        globalVar.server = Server(self.input_thread.sendServerCommand)

        # Start!
        self._startWebserver()
        self.input_thread.start()
        self.mc_server.startMCServer()

        # Catch KeyboardInterruption
        def stop_handler(signum, frame):
            print("Stopping gracefully...")
            try:
                self.mc_server.stopMCServer()
                self._stopWebserver()

            except Exception as e:
                print("Error: {}".format(e))
            
        # Handle interrupt signal
        signal.signal(signal.SIGINT, stop_handler)

        # Start daemon observer
        self.daemon = DaemonObserver()
        self.daemon.start()
    
    def _startWebserver(self) -> Process:
        # Start broadcast server process
        self._web_proc = Process(
            target=startBroadcastServer, 
            args = (config()["broadcast_port"], self.event_queue))
        self._web_proc.start()
        return self._web_proc
    
    def _stopWebserver(self):
        self._web_proc.terminate()
        self._web_proc.join()

    @abstractmethod
    def listen(self):
        ...

