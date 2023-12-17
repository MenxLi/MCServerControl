"""
Abstraction of the player
"""
import os, pickle, hashlib
from typing import Any, Optional
from .configReader import config
from .timeUtils import TimeUtils

class PlayerStatus:
    # default status
    is_online: bool
    time_login: float
    time_online: float                  # Total online time since server start (befor this login)
    time_online_today: float            # Total online time since today (befor this login)

    @property
    def record_dir(self):
        # save dir
        d = os.path.join(config()["world_conf_dir"], "player_status")
        if not os.path.exists(d):
            print("Created status record_dir: ", d)
            os.mkdir(d)
        return d

    def __init__(self, **kwargs) -> None:
        self.is_online = False
        self.time_login = TimeUtils.nowStamp()
        self.time_online = 0
        self.time_online_today = 0

        self.__keys = ["is_online", "time_login", "time_online", "time_online_today"] 
        self.__persistent_keys = ["time_login", "time_online", "time_online_today"]

        for k, v in kwargs.items():
            self.set(k, v)

    def setdefault(self, name: str, value: Any, persistent: Optional[bool] = None) -> Any:
        if not self.has(name):
            self.set(name, value, persistent)
            if name not in self.__keys:
                self.__keys.append(name)
        return self.get(name)

    def has(self, name):
        """
        use this instead of hasattr() to check value existance
        """
        return name in self.__keys

    def set(self, name: str, value: Any, persistent: Optional[bool] = None):
        """
         - persistent: will be saved to record_dir, so the value can be persistent after program exit
        """
        if name not in self.__keys:
            self.__keys.append(name)

        if persistent is not None:
            if persistent:
                if name not in self.__persistent_keys:
                    self.__persistent_keys.append(name)
            else:
                if name in self.__persistent_keys:
                    self.__persistent_keys.pop(self.__persistent_keys.index(name))

        setattr(self, name, value)

    def get(self, name: str) -> Any:
        return getattr(self, name)

    def toDict(self):
        d = {}
        for k in self.__keys:
            d[k] = self.get(k)
        return d

    def saveToFile(self, fname: str):
        """
        Save persistent status to self.record_dir/fname.status
        """
        st = dict()
        for k in self.__persistent_keys:
            st[k] = self.get(k)
        with open(os.path.join(self.record_dir, fname + ".status"), "wb") as fp:
            pickle.dump(st, fp)
        print("saved status record: ", fname)

    def loadFromFile(self, fname: str) -> bool:
        """
        Load persistent status from self.record_dir/fname.status
        """
        f_path = os.path.join(self.record_dir, fname + ".status")
        if not os.path.exists(f_path):
            print("No status file found ({}), skip loading".format(f_path))
            return False

        with open(f_path, "rb") as fp:
            st = pickle.load(fp)
        for k, v in st.items():
            self.set(k, v, persistent=True)
        print("loaded status record: ", fname)

        return True

    def __str__(self) -> str:
        return "PlayerStatus: " + str(self.toDict())

    __repr__ = __str__


class Player:
    def __init__(self, name: str, status_dict: dict = {}) -> None:
        self._name = name
        self.status = PlayerStatus(**status_dict)

    @property
    def name(self) -> str:
        return self._name

    @staticmethod
    def _hash(string: str) -> str:
        return hashlib.sha256(string.encode("utf-8")).hexdigest()[::2]

    def saveStatus(self):
        fname = self._hash(self.name)
        self.status.saveToFile(fname)

    def loadStatus(self):
        fname = self._hash(self.name)
        self.status.loadFromFile(fname)

