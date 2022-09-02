import json
import os

THIS_DIR = os.path.dirname(__file__)

# Read configuration
CONF_PATH = os.path.join(THIS_DIR, "config.json") 
CONF_PATH = os.path.abspath(CONF_PATH)

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
    CONF = json.load(fp)
    WORKING_DIR = os.path.abspath(CONF["server_dir"])
    ENTRY = CONF["entry"]
    BROADCAST_PORT = CONF["broadcast_port"]
    WORLD_NAME = CONF["world_name"]
