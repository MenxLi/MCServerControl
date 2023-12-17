from mcservercontrol.configReader import WORK_DIR, CONF_PATH, EXEC_PATH
import os, json, shutil, argparse

def init():
    if not os.path.exists(CONF_PATH):
        # Generate default configuation and exit
        with open(CONF_PATH, "w") as fp:
            _default_conf = {
                "server_dir": WORK_DIR,
                "entry": "java -Xmx1024M -Xms1024M -jar server.jar nogui",
                "world_name": "world",
                "broadcast_port": 25566,
            }
            json.dump(_default_conf, fp, indent=1)
        print("Generated default configuration file at: ", CONF_PATH)
    
    if not os.path.exists(EXEC_PATH):
        shutil.copyfile(
            os.path.join(os.path.dirname(__file__), '_script_template.py'),
            EXEC_PATH, 
        )
        print("Generated script file.")

    print("Please edit configuration and run `python .`")


def main():
    parser = argparse.ArgumentParser("MCServerControl")
    sp = parser.add_subparsers(dest="subparser")
    sp.add_parser("init", help = "initialization on current working directory.")
    args = parser.parse_args()
    if args.subparser == "init":
        init()
