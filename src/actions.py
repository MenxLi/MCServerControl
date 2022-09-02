import os, time, random
from typing import Any, Callable, List, TypedDict, Dict
from threading import Thread

from .configReader import WORKING_DIR, WORLD_NAME
from .timeUtils import TimeUtils
from src import timeUtils

class PlayerStatus(TypedDict):
    is_online: bool
    time_login: float
    time_online: float              # Total online time before last logout
    time_last_warn: float           # Warn player if they've been playing too long

class ServerActions:
    def __init__(self, cmd_input: Callable[[str], Any]) -> None:
        """
         - cmd_input: an interface to send command to the server
        """
        self.cmd = cmd_input

        # Record player status
        self.player_stats: dict[str, PlayerStatus] = dict()
        self.__startActionLoop()

    def showHelp(self, player_name: str):
        help_strs = [
            "suicide",
            "online-time",
            "save-world",
            "help",
        ]
        self.cmd("/tell {} Avaliable commands: {}".format(player_name, " | ".join(help_strs)))

    @staticmethod
    def schedule(func: Callable, delay: float, *args, **kwargs):
        """
        Delay execution of a function
        """
        def _f():
            time.sleep(delay)
            func(*args, **kwargs)
        Thread(target = _f, args=(), daemon = True).start()

    def __startActionLoop(self):
        """
        Perform some actions on every specific interval
        """
        LOOP_INTERVAL = 2 
        WARN_TOLERANCE =  3600
        WARN_INTERVAL = 1200
        def actionSchedule():
            # update user online time
            while True:
                for player_name in self.player_stats.keys():
                    player = self.player_stats[player_name]
                    if player["is_online"]:
                        time_since_last_login = TimeUtils.nowStamp() - player["time_login"]

                        if time_since_last_login > WARN_TOLERANCE and \
                                TimeUtils.nowStamp() - player["time_last_warn"] > WARN_INTERVAL:
                            self.cmd("/tell {} You have been playing for {} hours, is it too long?".format(
                                player_name, round(time_since_last_login/3600, 1)
                            ))
                            player["time_last_warn"] = TimeUtils.nowStamp()
                time.sleep(LOOP_INTERVAL)

        Thread(target=actionSchedule, args = (), daemon=True).start()

    def action_onLogin(self, player_name: str):
        # Maybe create a player status entry
        if player_name not in self.player_stats:
            self.player_stats[player_name] = {
                    "is_online": True,
                    "time_login": TimeUtils.nowStamp(),
                    "time_online": 0,
                    "time_last_warn": 0,
                }
            print("Created player status: ", player_name)
        else:
            # change status
            status = self.player_stats[player_name]
            status["is_online"] = True
            status["time_login"] = TimeUtils.nowStamp()

        self.action_sayHello(player_name)
        print(self.player_stats)

    def action_onLogout(self, player_name: str):
        self.cmd("/say Byebye {}.".format(player_name))

        # change status
        self.player_stats[player_name]["is_online"] = False
        self.player_stats[player_name]["time_online"] += TimeUtils.nowStamp() - self.player_stats[player_name]["time_login"]

    def action_sayHello(self, player_name):
        def sayWelcome():
            choices = ["Welcome", "Hello", "Greetings", "こんにちは", "欢迎", "Hola"]
            self.cmd("/title {} title {}".format(
                player_name, '{"text": "' + random.choice(choices) + '"}'
            ))
            self.cmd("/list")
        self.schedule(sayWelcome, 3)

    def action_saveWorld(self):
        """Make a backup of the world"""
        world_dir = os.path.join(WORKING_DIR, WORLD_NAME)
        if not os.path.exists(world_dir):
            self.cmd("/say saving faild, world (name:{}) not exists".format(WORLD_NAME))
            return
        self.cmd("/say Saving the world...")
        self.cmd("/save-all flush")
        ...

    def action_killPlayer(self, player_name: str):
        self.cmd(f"/kill {player_name}")

    def action_showPlayTime(self, player_name: str):
        player = self.player_stats[player_name]
        time_since_last_login = TimeUtils.nowStamp() - player["time_login"]
        time_total = player["time_online"] + time_since_last_login
        self.cmd("/tell {} Time online: {} hours (Total since server start: {} hours)".format(
            player_name, 
            round(time_since_last_login/3600, 2), 
            round(time_total/3600, 2)
        ))

