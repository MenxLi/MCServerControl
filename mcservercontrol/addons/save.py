from typing import List
from mcservercontrol.player import Player
from .. import PlayerCommandObserver

class CommandBackup(PlayerCommandObserver):

    def onTriggered(self, player: Player, _: List[str]):

        self.server.say("Backup the world (by - {})".format(player.name))
        self.server.backupWorld(remove_more_than=50)
    
    def help(self) -> str:
        return "Save the world, and make a backup"