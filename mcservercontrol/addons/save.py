from typing import List
from mcservercontrol.player import Player
from mcservercontrol.configReader import config
from .. import PlayerCommandObserver

class CommandBackup(PlayerCommandObserver):

    def onTriggered(self, player: Player, params: List[str]):

        if len(params) == 0:
            self.onInvalidArguments(player)
        
        cmd = params[0]

        if cmd == "now":
            self.server.say("Backup the world (by - {})".format(player.name))
            self.server.backupWorld(remove_more_than=config()["max_backup"])
        
        elif cmd == "list":
            to_tell = "List of backups for this world: \n"
            print(self.server.listBackups())
            self.server.tellraw(player, to_tell + "\n".join(self.server.listBackups()), color="gold")
        
        elif cmd == "rollback":
            if len(params)!=2:
                self.onInvalidArguments(player)
            self.server.loadBackup(params[1])
        
        else:
            self.onInvalidArguments(player)
    
    def help(self) -> str:
        to_show = [
            "Save the world, and make a backup. ", 
            f"Usage: {self.entry} [now] | [list] | [rollback <backup_name>]"
            "Examples: ",
            f" - {self.entry} now",
            f" - {self.entry} list",
            f" - {self.entry} rollback <backup_name>"
        ]
        return "\n".join(to_show)