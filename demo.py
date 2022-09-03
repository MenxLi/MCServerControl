from typing import Iterable
from src.player import Player
from src.observer import PlayerCommandObserver, PlayerObserver
from src.timeUtils import TimeUtils


class InitObserver(PlayerObserver):
    """
    Initializa player when they login
    You can add your own player status key in here

    ** This is a mandatory Observer to create player objects when they first login ** 
    """

    def onPlayerLogin(self, player: Player):
        return super().onPlayerLogin(player)


class WelcomeObserver(PlayerObserver):
    """
    Show welcome title after player logged in
    """
    def onPlayerLogin(self, player: Player):

        def welcome():
            self.server.title_setSubtitle(player, player.name)
            self.server.title(player, text = "Hello", color= "random")

        # Show welcome title 3 seconds after user login
        self.server.schedule(welcome, 3)

        return super().onPlayerLogin(player)

class GoodbyeObserver(PlayerObserver):
    """
    Inform everyone if any player is leaving
    """
    def onPlayerLogout(self, player: Player):
        for p in self.players.values():
            self.server.title(target=p, ttype="actionbar", text = f"Bye bye {player.name}.", color="yellow")

        return super().onPlayerLogout(player)

class CommandSuicide(PlayerCommandObserver):
    """
    A command to kill the player itself
    """
    def onTriggered(self, player: Player, args: Iterable):
        self.server.cmd(f"/kill {player.name}")
        return super().onTriggered(player, args)
    
    def help(self) -> str:
        # it is necessary to implement the help entry
        return "Kill your self"


class RemindAddictionCallback(PlayerObserver):
    """
    Remind player if anyone plays too long
    """
    def __call__(self):
        # The method will be added to daemon and run inside loop of another thread
        WARN_TOLERANCE =  3600
        WARN_INTERVAL = 900

        for player in self.players.values():
            # "time_last_warn" is not in player status by default
            if not hasattr(player.status, "time_last_warn"):
                setattr(player.status, "time_last_warn", 0)

            if player.status.is_online:
                time_since_last_login = TimeUtils.nowStamp() - player.status.time_login

                if time_since_last_login > WARN_TOLERANCE and \
                        TimeUtils.nowStamp() - getattr(player.status, "time_last_warn") > WARN_INTERVAL:
                    self.server.title(
                        target=player, 
                        ttype="actionbar",
                        color="yellow",
                        text="You have been playing for {} hours, is it too long?"\
                            .format(round(time_since_last_login/3600, 1))
                    )
                    setattr(player.status, "time_last_warn", TimeUtils.nowStamp())
