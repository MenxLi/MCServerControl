from typing import Iterable
from mcservercontrol.observer import PlayerObserver, PlayerCommandObserver
from mcservercontrol.player import Player
from mcservercontrol.timeUtils import TimeUtils

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
        # The method will be added to daemon and run inside loop of the listener.daemon thread
        WARN_TOLERANCE =  3600
        WARN_INTERVAL = 1200

        for player in self.players.values():
            # "time_last_warn" is not in player status by default
            player.status.setdefault("time_last_warn", 0)

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
                    player.status.time_last_warn = TimeUtils.nowStamp()

