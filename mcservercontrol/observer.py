from __future__ import annotations
from typing import Any, Callable, Dict, Iterable, List, Optional, Type, Union
from abc import abstractmethod, ABC
import time
from threading import Thread
from .timeUtils import TimeUtils
from .player import Player
from .server import Server
from . import globalVar


class Observer():
    subclasses: Dict[str, Type[Observer]] = {}

    def __init__(self) -> None:
        assert globalVar.server is not None, "Start minecraft server before initialize observers"
        self.server = globalVar.server

        self.cmd: Callable[[str], Any] = self.server.cmd

        # set when registered to the listerner
        self._all_players : dict[str, Player]

    @property
    def players(self) -> dict[str, Player]:
        return self._all_players

    def __init_subclass__(cls, name: Optional[str] = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if name:
            cls.subclasses[name] = cls

class PlayerObserver(Observer, ABC):
    def onPlayerLogin(self, player: Player):
        ...

    def onPlayerLogout(self, player: Player):
        ...

    def onPlayerSpeak(self, player: Player, content: str):
        ...

class PlayerCommandObserver(PlayerObserver, ABC):
    ALL : Dict[str, PlayerCommandObserver] = {}

    def __init__(self, entry: str) -> None:
        super().__init__()
        self.entry = entry
        self.ALL[entry] = self

    @abstractmethod
    def onTriggered(self, player: Player, args: Iterable):
        ...

    @abstractmethod
    def help(self) -> str:
        ...


class DaemonObserver(Observer):
    """
    An concurrency observer runing on another thread
    Will be triggered every certain interval
    """
    def __init__(self) -> None:
        super().__init__()

        self._callbacks: List[Callable] = []
        self._ob_interval = 1

    def setObserveInterval(self, interval: float):
        self._ob_interval = interval

    def addCallback(self, callback: Callable):
        self._callbacks.append(callback)

    def start(self):
        def _start():
            while True:
                for callback in self._callbacks:
                    callback()
                time.sleep(self._ob_interval)
        Thread(target=_start, args = (), daemon=True).start()

# ===========Below are some default observers=============

class OnlineTimeObserver(PlayerObserver):
    """
    Keep track of the player online time,
    Record them in player.status
    """
    def onPlayerLogin(self, player: Player):
        player.status.is_online = True
        player.status.time_login = TimeUtils.nowStamp()
        return super().onPlayerLogin(player)
    
    def onPlayerLogout(self, player: Player):
        player.status.is_online = False
        player.status.time_online += TimeUtils.nowStamp() - player.status.time_login
        return super().onPlayerLogout(player)

class CommandHelp(PlayerCommandObserver):
    """
    Show command help
    """
    def onTriggered(self, player: Player, args: Iterable):
        if not args:
            self.server.tellraw(player, self.help())
        else:
            entry = list(args)[0]
            if entry in self.ALL:
                self.server.tellraw(player, "Help for command - {}".format(entry), color="yellow")
                self.server.tellraw(player, self.ALL[entry].help())
            else:
                self.server.tellraw(player, "No such command - {}".format(entry), color="red")
                
        return super().onTriggered(player, args)

    def help(self):
        help_lines = [
            "Avaliable commands: "
        ]
        for entry in self.ALL.keys():
            help_lines.append(f" - {entry}")
        help_lines.append("To show help for specific command: \\\\help [entry]")
        return "\n".join(help_lines)


def getDefaultObservers() -> List[Union[PlayerObserver, PlayerCommandObserver]]:
    return [
        OnlineTimeObserver(),
        CommandHelp("help")
    ]

