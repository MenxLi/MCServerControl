"""
Abstraction of the player
"""
from typing import Any
from .timeUtils import TimeUtils

class PlayerStatus:
    # default status
    is_online: bool
    time_login: float
    time_online: float                  # Total online time since server start (befor this login)
    time_online_today: float            # Total online time since today (befor this login)

    def __init__(self, **kwargs) -> None:
        self.is_online = False
        self.time_login = TimeUtils.nowStamp()
        self.time_online = 0
        self.time_online_today = 0

        self.__keys = ["is_online", "time_login", "time_online", "time_online_today"] 
        for k, v in kwargs.items():
            self.set(k, v)

    def setdefault(self, name: str, value: Any) -> Any:
        if not self.has(name):
            setattr(self, name, value)
            if name not in self.__keys:
                self.__keys.append(name)
        return getattr(self, name)

    def has(self, name):
        """
        use this instead of hasattr() to check value existance
        """
        return name in self.__keys

    def set(self, name: str, value: Any):
        if name not in self.__keys:
            self.__keys.append(name)
        setattr(self, name, value)

    def get(self, name: str) -> Any:
        return getattr(self, name)

    def toDict(self):
        d = {}
        for k in self.__keys:
            d[k] = getattr(self, k)
        return d

    def __str__(self) -> str:
        return "PlayerStatus: " + str(self.toDict())

    __repr__ = __str__


class Player:
    def __init__(self, name: str, status_dict: dict = {}) -> None:
        self._name = name
        self.status = PlayerStatus(**status_dict)

    @property
    def name(self):
        return self._name

