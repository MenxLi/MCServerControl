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

class GoodbyeObserver(PlayerObserver):
    """
    Inform everyone if any player is leaving
    """
    def onPlayerLogout(self, player: Player):
        for p in self.players.values():
            # p is player, traverse all players and inform everyone
            self.server.title(target=p, ttype="actionbar", text = f"Bye bye {player.name}.", color="aqua")

        return super().onPlayerLogout(player)

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

class CommandOnlineTime(PlayerCommandObserver):
    """
    Show player online time
    """
    def onTriggered(self, player: Player, args: Iterable):
        time_since_last_login = TimeUtils.nowStamp() - player.status.time_login
        time_total = player.status.time_online + time_since_last_login
        to_show = "Time online: {} hours \nTotal since server start: {} hours".format(
            round(time_since_last_login/3600, 2), 
            round(time_total/3600, 2)
        )
        self.server.tellraw(player, to_show, color="yellow")
        return super().onTriggered(player, args)

    def help(self) -> str:
        return "Show online time (since last login and since server start)"

class RemindAddictionCallback(PlayerObserver):
    """
    Remind player if anyone plays too long
    """
    def __call__(self):
        # The method will be added to daemon and run inside loop of another thread
        WARN_TOLERANCE =  3600
        WARN_INTERVAL = 1200

        for player in self.players.values():
            # "time_last_warn" is not in player status by default
            if not hasattr(player.status, "time_last_warn"):
                setattr(player.status, "time_last_warn", 0)

            if player.status.is_online:
                time_since_last_login = TimeUtils.nowStamp() - player.status.time_login

                if time_since_last_login > WARN_TOLERANCE and \
                        TimeUtils.nowStamp() - getattr(player.status, "time_last_warn") > WARN_INTERVAL:
                    self.server.tellraw(
                        target = player,
                        color = "red",
                        text = "You have been playing for {} hours, is it too long?"\
                            .format(round(time_since_last_login/3600, 1))
                    )
                    setattr(player.status, "time_last_warn", TimeUtils.nowStamp())

