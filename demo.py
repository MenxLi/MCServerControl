import random
from typing import Iterable
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

class CommandSuicide(PlayerCommandObserver):
    """
    A command to kill the player itself
    """
    def onTriggered(self, player: Player, args: Iterable):
        # Using server.cmd to send native minecraft server command
        self.server.cmd(f"/kill {player.name}")
        return super().onTriggered(player, args)
    
    def help(self) -> str:
        # it is necessary to implement the help entry
        return "Kill your self"
