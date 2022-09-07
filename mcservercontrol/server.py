"""
An abstraction of the minecraft server actions
"""

from typing import Any, Callable, Literal, Tuple
import time, random, os
from threading import Thread
from .configReader import config
from .player import Player

COLOR_T = Literal[
    "white", 
    "yellow",
    "light_purple",
    "red",
    "aqua",
    "green",
    "blue",
    "gray",
    "gold",
    "dark_purple",
    "dark_red",
    "dark_aqua",
    "dark_green",
    "dark_blue",
    "dark_gray",
    "black",
    "minecoin_goid",

    "random",
]

class Server:
    def __init__(self, cmd_interface: Callable[[str], Any]) -> None:
        """
        - command_interface: method to pass command to minecraft server
        """
        self._cmd = cmd_interface

    @property
    def cmd(self) -> Callable[[str], Any]:
        return self._cmd

    @staticmethod
    def schedule(func: Callable, delay: float, *args, **kwargs):
        """
        Delay execution of a function
        """
        def _f():
            time.sleep(delay)
            func(*args, **kwargs)
        Thread(target = _f, args=(), daemon = True).start()

    @staticmethod
    def randomHexColor() -> str:
        color = "%06x" % random.randint(0, 0xFFFFFF)
        return "#" + color
    
    def _mapColor(self, color: COLOR_T) -> str:
        if color == "random":
            color_ = self.randomHexColor()
        else:
            color_ = color
        return color_

    def title(self, 
              target: Player,
              text: str, 
              ttype: Literal["title", "actionbar"] = "title",
              color: COLOR_T = "white", 
              ):
        self.cmd(f'/title {target.name} {ttype} {{"text": "{text}", "color": "{self._mapColor(color)}"}}')

    def title_setSubtitle(self, 
                    target: Player,
                    text: str, 
                    color: COLOR_T = "white", 
                    ):
        self.cmd(f'/title {target.name} subtitle {{"text": "{text}", "color": "{self._mapColor(color)}"}}')

    def title_setTime(self, 
                        target: Player,
                        times: Tuple[float, float, float] = (10,30,10),  # fadeIn, stay fadeout
                     ):
        """
        times in 0.1 seconds
        """
        self.cmd(f'/title {target.name} times {times[0]} {times[1]} {times[2]}')

    def title_reset(self, target: Player):
        self.cmd(f'/title {target.name} reset')

    def title_clear(self, target: Player):
        self.cmd(f'/title {target.name} clear')

    def tellraw(self, target: Player, text: str, color: COLOR_T = "white"):
        text = text.replace("\n", "\\n")
        self.cmd(f'/tellraw {target.name} {{"text": "{text}", "color": "{self._mapColor(color)}"}}')

    def say(self, text: str):
        self.cmd(f"/say {text}")

    def saveWorld(self):
        """Make a backup of the world"""
        world_dir = os.path.join(config["server_dir"], config["world_name"])
        if not os.path.exists(world_dir):
            self.cmd("/say saving faild, world (name:{}) not exists".format(config["world_name"]))
            return
        self.cmd("/say Saving the world...")
        self.cmd("/save-all flush")
