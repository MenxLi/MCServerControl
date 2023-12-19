from typing import List
from mcservercontrol.observer import Observer, PlayerObserver, PlayerCommandObserver
from mcservercontrol.player import Player
from mcservercontrol.timeUtils import TimeUtils

def getOnlineTime(player: Player):
    now_stamp = TimeUtils.nowStamp()
    time_since_last_login = now_stamp - player.status.time_login
    time_since_today = time_since_last_login + player.status.time_online_today
    time_total = player.status.time_online + time_since_last_login

    return {
        "this": time_since_last_login,
        "today": time_since_today,
        "total": time_total
    }

class CommandOnlineTime(PlayerCommandObserver):
    """
    Show player online time
    """
    def onTriggered(self, player: Player, args: List[str]):
        if not args:
            online = getOnlineTime(player)
            to_show = "Time online: {} hours \nTime today: {} hours \nTotal: {} hours".format(
                round(online["this"]/3600, 2), 
                round(online["today"]/3600, 2),
                round(online["total"]/3600, 2),
            )
            self.server.tellraw(player, to_show, color="yellow")

        elif args[0] == "warn" and len(args) == 2:
            if player.status.has("time_warn_flag"):
                if args[1] == "on":
                        player.status.set("time_warn_flag", True)
                        self.server.tellraw(player, "Enable online time reminder.", color="yellow")
                if args[1] == "off":
                        player.status.set("time_warn_flag", False)
                        self.server.tellraw(player, "Disable online time reminder.", color="yellow")
            else:
                self.server.tellraw(player, "NO online-time reminder find.", color="red")

        elif args[0] == "clear":
            player.status.time_online = 0
            player.status.time_online_today = 0
            if "RemindAddictionCallback" in Observer.subclasses:
                print("Clearing ra_callback_cls")
                ra_callback_cls: RemindAddictionCallback = Observer.subclasses["RemindAddictionCallback"]
                ra_callback_cls.resetStatus(player)

            self.server.tellraw(player, "Cleared online-time record", color="white")

        else:
            self.onInvalidArguments(player)

        return super().onTriggered(player, args)

    def help(self) -> str:
        to_show = [
            "Show online time",
            "Usage: online-time [warn on/off] | [clear]",
            "Examples: ",
            " - {} : show online time".format(self.entry),
            " - {} warn off : disable addiction warning".format(self.entry),
            " - {} clear : clear online time record before this login".format(self.entry),
        ]
        return "\n".join(to_show)

class RemindAddictionCallback(PlayerObserver, flag = "RemindAddictionCallback"):
    """
    Online time reminder
    Remind player if anyone plays too long
    """
    def onPlayerLogin(self, player: Player):
        player.status.setdefault("time_last_warn", 0, persistent=True)
        player.status.setdefault("time_warn_flag", True, persistent=True)    # Indicates whether to show warning

    @classmethod
    def resetStatus(cls, player):
        player.status.set("time_last_warn", 0, persistent=True)
        player.status.set("time_warn_flag", True, persistent=True)

    def __call__(self):
        # The method will be added to daemon and run inside loop of the listener.daemon thread
        WARN_TOLERANCE =  3600
        WARN_INTERVAL = 1200

        for player in self.players.values():
            # "time_last_warn" is not in player status by default

            if player.status.is_online and player.status.get("time_warn_flag"):
                online_time = getOnlineTime(player)
                time_today = online_time["today"]

                if time_today > WARN_TOLERANCE and \
                        TimeUtils.nowStamp() - player.status.get("time_last_warn") > WARN_INTERVAL:
                    self.server.tellraw(
                        target = player,
                        color = "red",
                        text = "You have been playing for {} hours today, is it too long?"\
                            .format(round(time_today/3600, 1))
                    )
                    player.status.set("time_last_warn", TimeUtils.nowStamp())

