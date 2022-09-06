"""
Abstraction of the player
"""
from typing import Any
from .timeUtils import TimeUtils

class PlayerStatus:

    def __init__(self, **kwargs) -> None:
        self.is_online: bool = True
        self.time_login: float = TimeUtils.nowStamp()
        self.time_online: float = 0                    # Total online time since server start (befor this login)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def setdefault(self, name: str, value: Any) -> Any:
        if not hasattr(self, name):
            setattr(self, name, value)
        return getattr(self, name)

    # For dynamically type checking
    def __getattr__(self, name: str) -> Any: ...

    def __setattr__(self, name: str, value: Any) -> None: ...

class Player:
    def __init__(self, name: str, status_dict: dict = {}) -> None:
        self._name = name
        self.status = PlayerStatus(**status_dict)

    @property
    def name(self):
        return self._name

