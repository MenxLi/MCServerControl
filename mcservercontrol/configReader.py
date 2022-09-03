import json
import os
from typing import TypedDict

THIS_DIR = os.path.dirname(__file__)

# Read configuration
CONF_PATH = os.path.join(THIS_DIR, "config.json") 
CONF_PATH = os.path.abspath(CONF_PATH)

class CONF_T(TypedDict):
    server_dir: str
    entry: str
    world_name: str
    broadcast_port: int

if not os.path.exists(CONF_PATH):
    # Generate default configuation and exit
    with open(CONF_PATH, "w") as fp:
        _default_conf = {
            "server_dir": "",
            "entry": "java -Xmx1024M -Xms1024M -jar server.jar nogui",
            "world_name": "world",
            "broadcast_port": 25566,
        }
        json.dump(_default_conf, fp, indent=1)
    print("Generated default configuration file at: ", CONF_PATH)
    print("Please edit configuration and re-start this script")
    exit()


with open(CONF_PATH, "r") as fp:
    config: CONF_T = json.load(fp)

_version_histories = [
    ("0.0.1", "init"),
    ("0.1.0", "Re-written with new abstractions: player, server, observer and listener")
]

VERSION, UPDATE_NOTE = _version_histories[-1]
