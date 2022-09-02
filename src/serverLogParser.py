"""
Parse minecraft server log to events
"""
from __future__ import annotations
import re
from typing import List, Literal, TypedDict, Union, overload, Any, Type
from .timeUtils import TimeUtils

EVENT_TYPE = Literal[
    "login", 
    "logout",
    "listplayer",
    "cmd",
    "unknown", 
]

class _EVENT_BASE(TypedDict):
    etype: EVENT_TYPE
    time: float                 # time stamp
    log_line: str               # original log

class EVENT_UNKNOWN(_EVENT_BASE):
    ...

class EVENT_LOGIN(_EVENT_BASE):
    user_name: str

class EVENT_LOGOUT(_EVENT_BASE):
    user_name: str

class EVENT_CMD(_EVENT_BASE):
    # user command
    user_name: str
    cmd: List[str]

class EVENT_LISTPLAYER(_EVENT_BASE):
    all_players: str

class EVENT_ALL(_EVENT_BASE, total = False):
    # All possible entries
    user_name: str
    all_players: str
    cmd: List[str]


def splitLogLineBySB(line: str) ->List[str]:
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

def parseLine(line: str) -> EVENT_ALL:
    line_split = splitLogLineBySB(line)

    event: EVENT_ALL = {
        "etype": "unknown",
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

    if "joined the game" in content:
        event["etype"] = "login"
        event["user_name"] = content.split("joined the game")[0].strip()

    elif "left the game" in content:
        event["etype"] = "logout"
        event["user_name"] = content.split("left the game")[0].strip()

    elif "There are" in content and "players online:":
        event["etype"] = "listplayer"
        event["all_players"] = content.split("players online:")[1].strip("\n")
        
    elif re.match(r"\<[^\<]*\>", content):
        match = re.match(r"\<[^\<]*\>", content)
        assert match is not None
        user_name = content[match.start()+1: match.end()-1]
        words = content[match.end()+1:]
        if words.startswith("\\"):
            event["etype"] = "cmd"
            event["user_name"] = user_name
            cmd_split = words[1:].strip("\n").split(" ")
            event["cmd"] = cmd_split

    return event
