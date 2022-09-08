from typing import List
from mcservercontrol.observer import PlayerCommandObserver
from mcservercontrol.player import Player


class CommandTeleportPlayer(PlayerCommandObserver):

    def onTriggered(self, player: Player, args: List[str]):
        if len(args) != 1:
            self.onInvalidArguments(player)
            return super().onTriggered(player, args)

        name_raw = args[0]
        name_pool: List[str] = [ p.name for p in self.players.values() if p.status.is_online ]
        dst_name = None

        if name_raw in name_pool:
            dst_name = name_raw

        else:
            # Name infer
            possible_names = [ n for n in name_pool if n.startswith(name_raw)]

            if len(possible_names) == 1:
                dst_name = possible_names[0]

            elif len(possible_names) == 0:
                # No name found
                self.server.tellraw(
                    target=player,
                    text = "No matching player found",
                    color="red"
                )
                self.onInvalidArguments(player)
            else:
                # Multiple names found
                self.server.tellraw(
                    target=player,
                    text = "Ambiguity on player name: {}?".format(
                        " (or) ".join(possible_names)
                    ),
                    color="red"
                )
                self.onInvalidArguments(player)

        if dst_name:
            self.server.cmd(f"/tp {player.name} {dst_name}")
            self.server.say(f"Teleported {player.name} to {dst_name}.")

        return super().onTriggered(player, args)


    def help(self) -> str:
        to_show = [
            "Teleport yourself to another player",
            "Example: ", 
            "\t {} Alex : Teleport yourself to Alex".format(self.entry),
            "\t {} A : Teleport yourself to Alex - Alex will be inferred out of A".format(self.entry)
        ]
        return "\n".join(to_show)
