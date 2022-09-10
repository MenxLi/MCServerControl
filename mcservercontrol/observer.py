from __future__ import annotations
import json
from typing import Any, Callable, Dict, List, Optional, Type, Union
from abc import abstractmethod, ABC
import time
from threading import Thread

from mcservercontrol.server import COLOR_T
from .configReader import VERSION
from .timeUtils import TimeUtils
from .player import Player
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

    def __init__(self, entry: str, alias: List[str] = []) -> None:
        super().__init__()
        self.entry = entry
        self.ALL[entry] = self
        self.alias = alias

    @abstractmethod
    def onTriggered(self, player: Player, args: List[str]):
        ...

    @abstractmethod
    def help(self) -> str:
        ...

    def showHelp(self, player: Player, color: COLOR_T = "aqua"):
        self.server.tellraw(
            target = player,
            text = self.help(),
            color = color
        )

    def onInvalidArguments(self, player: Player):
        self.server.tellraw(
            target = player,
            text = "Invalid arguments! \nUsage: ",
            color = "red"
        )
        self.showHelp(player, "yellow")


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
        # previous login date
        prev_login = TimeUtils.stamp2Local(player.status.time_login).date()

        player.status.is_online = True
        player.status.time_login = TimeUtils.nowStamp()

        this_login = TimeUtils.stamp2Local(player.status.time_login).date()
        if prev_login != this_login:
            # login in another day, reset daily online time
            player.status.time_online_today = 0

        return super().onPlayerLogin(player)
    
    def onPlayerLogout(self, player: Player):
        player.status.is_online = False
        this_online_time = TimeUtils.nowStamp() - player.status.time_login
        player.status.time_online += this_online_time
        player.status.time_online_today += this_online_time

        return super().onPlayerLogout(player)

class DisplayVersionObserver(PlayerObserver):
    def onPlayerLogin(self, player: Player):
        self.server.tellraw(
            target=player, 
            text="MCServerControl version - {}".format(VERSION),
            color="aqua"
        )
        return super().onPlayerLogin(player)

class DisplayVersionCommand(PlayerCommandObserver):
    def onTriggered(self, player: Player, args: List[str]):
        self.server.tellraw(
            target=player, 
            text="MCServerControl version - {}".format(VERSION),
            color="aqua"
        )
        return super().onTriggered(player, args)
    
    def help(self) -> str:
        return "Show MCServerControl version."

class CommandHelp(PlayerCommandObserver):
    """
    Show command help
    """
    def onTriggered(self, player: Player, args: List[str]):
        if not args:
            self.showHelp(player)
        else:
            entry = list(args)[0]
            if entry in self.ALL:
                self.server.tellraw(player, "Help for command - {}".format(entry), color="yellow")
                self.ALL[entry].showHelp(player)
            else:
                self.server.tellraw(player, "No such command - {}".format(entry), color="red")
                
        return super().onTriggered(player, args)

    def help(self):
        help_lines = [
            "Avaliable commands (alias in parentheses): "
        ]
        for entry, ob in self.ALL.items():
            if ob.alias:
                alias_str = ", ".join(ob.alias)
                help_lines.append(f" - {entry} ({alias_str})")
            else:
                help_lines.append(f" - {entry}")
        help_lines.append("To show help for specific command: \\\\help [entry]")
        return "\n".join(help_lines)


def getDefaultObservers() -> List[Union[PlayerObserver, PlayerCommandObserver]]:
    return [
        OnlineTimeObserver(),
        DisplayVersionObserver(),
        DisplayVersionCommand("version"),
        CommandHelp("help")
    ]

