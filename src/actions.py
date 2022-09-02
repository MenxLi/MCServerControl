import os, time, random
from typing import Any, Callable, List
from threading import Thread

from .configReader import WORKING_DIR, WORLD_NAME

class ServerActions:
    def __init__(self, cmd_input: Callable[[str], Any]) -> None:
        """
         - cmd_input: an interface to send command to the server
        """
        self.cmd = cmd_input

    @staticmethod
    def schedule(func: Callable, delay: float, *args, **kwargs):
        """
        Delay execution of a function
        """
        def _f():
            time.sleep(delay)
            func(*args, **kwargs)
        Thread(target = _f, args=(), daemon = True).start()

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
            self.cmd("/tell saving faild, world (name:{}) not exists".format(WORLD_NAME))
            return
        ...

    def action_killPlayer(self, player_name: str):
        self.cmd(f"/kill {player_name}")

