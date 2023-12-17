import json
import os, sys
from typing import TypedDict

WORK_DIR = os.path.abspath(os.path.realpath(os.getcwd()))

# Read configuration
CONF_PATH = os.path.join(WORK_DIR, "mcservercontrol.json") 
EXEC_PATH = os.path.join(WORK_DIR, "__main__.py")

class CONF_T(TypedDict):
    server_dir: str
    entry: str
    world_name: str
    broadcast_port: int

    # Entries inferred from config file
    world_dir: str              # /server_dir/world_name
    world_conf_dir: str         # /server_dir/world_name/.mcservercontrol

__config_cache = None
def config():
    global __config_cache
    if __config_cache:
        return __config_cache
    if os.path.exists(CONF_PATH):
        with open(CONF_PATH, "r") as fp:
            config_raw = json.load(fp)
    else:
        raise FileNotFoundError("No configuration")

    # world directory
    cfg: CONF_T = config_raw.copy()
    cfg["world_dir"] = os.path.join(cfg["server_dir"], cfg["world_name"])
    if not os.path.exists(cfg["world_dir"]):
        print("Created world directory...")
        os.mkdir(cfg["world_dir"])
    # world configuration directory
    _world_conf_dir = os.path.join(cfg["server_dir"], cfg["world_name"], ".mcservercontrol")
    if not os.path.exists(_world_conf_dir):
        os.mkdir(_world_conf_dir)
    cfg["world_conf_dir"] = _world_conf_dir

    __config_cache = cfg
    return cfg

_version_histories = [
    ("0.0.1", "init"),
    ("0.1.0", "Re-written with new abstractions: player, server, observer and listener"),
    ("0.1.1", "Player status using get/set, record player today's online time"), 
    ("0.1.2", "Record scheduled task globally; showHelp method; warn invalid command; addons"), 
    ("0.1.3", "Added mcservercontrol world config directory; persistent player status"), 
    ("0.1.4", "Use mcservercontrol.json at cwd as configuration file; use python module"),
]

VERSION, UPDATE_NOTE = _version_histories[-1]
