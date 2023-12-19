from typing import List
from mcservercontrol.observer import PlayerCommandObserver
from mcservercontrol.player import Player
from mcservercontrol.server import SCHEDULE_ID
from mcservercontrol import globalVar

class CommandKillItem(PlayerCommandObserver):
    """
    Command to kill all items
    """
    def onPlayerLogin(self, player: Player):

        player.status.setdefault("kill_item_thread_ids", [])

        return super().onPlayerLogin(player)


    def onTriggered(self, player: Player, args: List[str]):

        k_ids: List[SCHEDULE_ID] = player.status.get("kill_item_thread_ids")

        def _killItems():
            self.server.cmd("/kill @e[type=item]")
            self.server.say(f"Killed all items. (Triggered by {player.name})")

        def _checkAlive():
            for i in range(len(k_ids))[::-1]:
                t_id = k_ids[i]
                if not t_id in globalVar.scheduled_threads:
                    # stopped
                    k_ids.pop(i)

        if not args:
            # By default, kill all items in 1 minute
            self.server.say("Will clear items in 1 minute.")
            k_id = self.server.schedule(_killItems, 60)
            k_ids.append(k_id)

        elif args[0].isnumeric():
            # Schedule a item kill command
            delay = float(args[0])
            self.server.say(f"Will clear items in {round(delay, 1)} seconds. (Triggered by {player.name})")
            k_id = self.server.schedule(_killItems, delay)
            k_ids.append(k_id)

        elif args[0] == "now":
            # Kill item instantly
            _killItems()

        elif args[0] == "stop":
            # Stop possibe scheduled item kill commands, triggered by this player
            _checkAlive()
            if k_ids:
                for t_id in k_ids:
                    thread = globalVar.scheduled_threads[t_id]
                    thread.stop()
                player.status.set("kill_item_thread_ids", [])

                self.server.say(f"Stopped kill item schedule ({player.name})")
            else:
                self.server.tellraw(
                    target=player,
                    text="You have not started kill-item schedule",
                    color="red"
                )

        else:
            self.onInvalidArguments(player)

        return super().onTriggered(player, args)

    def help(self) -> str:
        to_show = [
            "Kill all items, usage: {} [now | <delay> | stop]".format(self.entry),
            "By default delay=60s",
            "Use now to kill items instantly",
            "Use stop to stop scheduled kill item commands",
            "Examples: ",
            " - {} now : Kill item instantly".format(self.entry),
            " - {} 30 : Kill item in 30s".format(self.entry),
            " - {} stop : Stop scheduled kill-item".format(self.entry),
        ]
        return "\n".join(to_show)
