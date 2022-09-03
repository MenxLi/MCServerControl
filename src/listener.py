import os, signal, re
from warnings import warn
from typing import IO, List
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from multiprocessing import Queue, Process

from .listenerBase import *
from .timeUtils import TimeUtils
from .configReader import config
from .broadcastServer import startServer as startBroadcastServer
from . import globalVar; globalVar.init()

class EventListener(EventListenerBase):

    @property
    def cmd_interface(self) -> Callable[[str], Any]:
        if hasattr(self, "input_thread"):
            return self.input_thread.sendServerCommand
        else:
            return lambda x: warn("Minecraft command line interface not ready.")

    def listen(self):
        while self.proc.poll() is None:
            # Log listening loop
            output = self.proc.stdout.readline()
            if output:
                self.parse(output.decode("utf-8"))

        self.proc.stdout.close()
        self.proc.stdin.close()
        exit(self.proc.poll())

    def parse(self, line: str):
        line_split = self._splitLogLineBySB(line)

        event: EVENT_ALL = {
            "etype": "general",
            "time": TimeUtils.nowStamp(),
            "log_line": line
        }

        if len(line_split)<4 or not (
            line_split[0].startswith("[") and 
            line_split[2].startswith("[") and 
            line_split[3].startswith(": ")
        ):
            # unknown
            return event

        # Analyse content
        line_split[3] = line_split[3][2:]
        content = "".join(line_split[3:])

        # Player login
        if "joined the game" in content:
            event["etype"] = "login"
            name = content.split("joined the game")[0].strip()
            if name not in self.players.keys():
                # create the player object on their first login
                self.players[name] = Player(name, status_dict={"is_online": True})
            player = self.players[name]
            event["player"] = player

        # Player logout
        elif "left the game" in content:
            event["etype"] = "logout"
            name = content.split("left the game")[0].strip()
            event["player"] = self.players[name]

        elif re.match(r"^There are \d* of a max of \d* players online:.*", content):
            event["etype"] = "listplayer"
            player_names = content.split("players online:")[1].strip("\n").split(",")
            event["players"] = [self.players[p_name.strip()] for p_name in player_names ]
            
        #Player enter command or speak
        elif re.match(r"\<[^\<]*\>", content):
            match = re.match(r"\<[^\<]*\>", content)
            assert match is not None
            name = content[match.start()+1: match.end()-1]
            player = self.players[name]
            words = content[match.end()+1:]
            if words.startswith("\\"):
                event["etype"] = "cmd"
                event["player"] = player
                cmd_raw_split: List[str] = words[1:].strip("\n").split(" ")
                cmd_name = cmd_raw_split[0]
                if len(cmd_raw_split) == 0:
                    cmd_split = (cmd_name, [])
                else:
                    cmd_split = (cmd_name, cmd_raw_split[1:])
                event["cmd_split"] = cmd_split
            else:
                event["etype"] = "speak"
                event["player"] = player
                event["content"] = words

        self.emit(event)

    def _splitLogLineBySB(self, line: str) -> List[str]:
        """Split by square brackets"""
        sb_span = []
        for match in re.finditer(r"\[[^[^\]]*\]", line):
            sb_span.append(match.span())
        if not sb_span:
            # blank
            return []
        
        split = []
        idx = 0
        for sp in sb_span:
            if sp[0]>idx:
                split.append(line[idx: sp[0]])
            split.append(line[sp[0]: sp[1]])
            idx = sp[1]
        if idx < len(line)-1:
            split.append(line[idx:])
        return split
