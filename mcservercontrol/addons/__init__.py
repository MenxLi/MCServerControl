"""
Some preset observers
"""

import random
from typing import Iterable, List
from mcservercontrol import Player, PlayerObserver, PlayerCommandObserver
from mcservercontrol.timeUtils import TimeUtils


class WelcomeObserver(PlayerObserver):
    """
    Show random welcome title after player logged in
    """
    def onPlayerLogin(self, player: Player):

        def welcome():
            choices = ["Welcome", "Hello", "Greetings", "你好", "欢迎", "哈咯"]
            self.server.title(player, text = random.choice(choices), color= "random")
            self.server.title_setSubtitle(player, player.name)

        # Show welcome title 3 seconds after user login
        self.server.schedule(welcome, 3)

        return super().onPlayerLogin(player)

class GoodbyeObserver(PlayerObserver):
    """
    Inform everyone if any player is leaving
    """
    def onPlayerLogout(self, player: Player):
        self.server.cmd(f"/say Goodbye, {player.name}")

        return super().onPlayerLogout(player)

class CommandSuicide(PlayerCommandObserver):
    """
    A command to kill the player itself
    """
    def onTriggered(self, player: Player, args: List[str]):
        # Using server.cmd to send native minecraft server command
        self.server.cmd(f"/kill {player.name}")
        return super().onTriggered(player, args)
    
    def help(self) -> str:
        # it is necessary to implement the help entry
        return "Kill your self"


class CommandKillItem(PlayerCommandObserver):
    """
    Command to kill all items
    """

    def onTriggered(self, player: Player, args: List[str]):

        def _killItems():
            self.server.cmd("/kill @e[type=item]")
            self.server.say("Killed all items.")

        if not args:
            self.server.say("Will clear items in 1 minute.")
            self.server.schedule(_killItems, 60)

        elif args[0] == "now":
            _killItems()

        elif args[0].isnumeric():
            delay = float(args[0])
            self.server.say(f"Will clear items in {round(delay, 1)} seconds.")
            self.server.schedule(_killItems, delay)

        else:
            self.onInvalidArguments(player)

        return super().onTriggered(player, args)

    def help(self) -> str:
        to_show = [
            "Kill all items, usage: {} [now/<delay>]".format(self.entry),
            "By default delay=60s"
        ]
        return "\n".join(to_show)
