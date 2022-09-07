from typing import List
from mcservercontrol.observer import PlayerCommandObserver
from mcservercontrol.player import Player

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
