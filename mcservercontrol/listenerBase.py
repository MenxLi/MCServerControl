from abc import abstractmethod
from typing import Any, Callable, Dict, Literal, Tuple, TypedDict, List, Union, IO
import os, warnings, signal
from multiprocessing import Process, Queue
from subprocess import Popen, PIPE, STDOUT
from threading import Thread

from mcservercontrol import globalVar
from mcservercontrol.server import Server

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

class MCPopen(Popen):
    # Type checking purpose
    stdin: IO[bytes]
    stdout: IO[bytes]


class InputThread(Thread):
    """
    Thread listening to user input from console
    """
    def __init__(self, mc_proc: MCPopen) -> None:
        """
         - mc_proc: minecraft server process
        """
        # daemon thread will end when main thread exit
        super().__init__(daemon=True)
        self._mc_proc = mc_proc

    @property
    def mc_proc(self):
        return self._mc_proc

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

        self.input_thread: InputThread
        self.daemon: DaemonObserver
        self.proc: MCPopen
        self.event_queue: Queue

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
            ...

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
                self.player_command_observers[entry].onTriggered(
                    event["player"], event["cmd_split"][1]
                )
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

        self.proc = MCPopen(config()["entry"].split(" "), stdout = PIPE, stdin = PIPE, stderr = STDOUT)

        # Start a thread that listen to user input
        self.input_thread = InputThread(self.proc)
        self.input_thread.start()

        # Save server to global variable to be accessed by observers
        globalVar.server = Server(self.input_thread.sendServerCommand)

        # Start broadcast server process
        self.event_queue = Queue()
        broadcast_proc = Process(
            target=startBroadcastServer, 
            args = (config()["broadcast_port"], self.event_queue))
        broadcast_proc.start()

        # Catch KeyboardInterruption
        def stop_handler(signum, frame):
            print("Stopping gracefully...")
            try:
                self.stopMCServer()
                broadcast_proc.terminate()
                broadcast_proc.join()

            except Exception as e:
                print("Error: {}".format(e))
            
        # Handle interrupt signal
        signal.signal(signal.SIGINT, stop_handler)

        # Start daemon observer
        self.daemon = DaemonObserver()
        self.daemon.start()
    
    def stopMCServer(self):
        # send command to minecraft server to stop gracefully
        self.proc.stdin.write(b"stop\n")
        self.proc.stdin.flush()
        self.proc.wait()
        print("Stopped minecraft server.")

    @abstractmethod
    def listen(self):
        ...

