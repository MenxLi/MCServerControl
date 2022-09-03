"""
Abstraction of the player
"""
from .timeUtils import TimeUtils

class PlayerStatus:

    def __init__(self, **kwargs) -> None:
        self.is_online: bool = True
        self.time_login: float = TimeUtils.nowStamp()
        self.time_online: float = 0                    # Total online time since server start (befor this login)
        for k, v in kwargs.items():
            setattr(self, k, v)


class Player:
    def __init__(self, name: str, status_dict: dict = {}) -> None:
        self._name = name
        self.status = PlayerStatus(**status_dict)

    @property
    def name(self):
        return self._name

