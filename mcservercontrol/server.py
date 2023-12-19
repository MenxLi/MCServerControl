"""
An abstraction of the minecraft server actions
"""

from typing import Any, Callable, Literal, Tuple, NewType, Optional, IO
from subprocess import Popen, PIPE, STDOUT
import time, random, os, shutil, zipfile
from threading import Thread
import uuid
from . import globalVar
from .configReader import config
from .player import Player

class MCPopen(Popen):
    # Type checking purpose
    stdin: IO[bytes]
    stdout: IO[bytes]


COLOR_T = Literal[
    "white", 
    "yellow",
    "light_purple",
    "red",
    "aqua",
    "green",
    "blue",
    "gray",
    "gold",
    "dark_purple",
    "dark_red",
    "dark_aqua",
    "dark_green",
    "dark_blue",
    "dark_gray",
    "black",
    "minecoin_goid",

    "random",
]

SCHEDULE_ID = NewType("SCHEDULE_ID", str)

def newScheduleID() -> SCHEDULE_ID:
    return SCHEDULE_ID(uuid.uuid4().hex)

class ScheduleThread(Thread):
    def __init__(self, sid: SCHEDULE_ID, target: Callable[[], None], delay: float) -> None:
        super().__init__(target = target, daemon=True)
        self.id = sid
        self._target = target
        self._delay = delay
        self._stop_flag = False
        self.stopped = False

        # add to scheduled_threads pool
        globalVar.scheduled_threads[self.id] = self

    def run(self) -> None:
        time.sleep(self._delay)
        if not self._stop_flag:
            self._target()
        self._onStop()

    def stop(self):
        self._stop_flag = True
        self._onStop()

    def _onStop(self):
        self.stopped = True
        # Clear from global thread_id pool
        if self.id in globalVar.scheduled_threads:
            del globalVar.scheduled_threads[self.id]

class Server:
    def __init__(self, cmd_interface: Callable[[str], Any]) -> None:
        """
        - command_interface: method to pass command to minecraft server
        """
        self._cmd = cmd_interface
        self._proc: MCPopen         # minecraft process
        self.onWorldSaveCallback = lambda : None
    
    @property
    def proc(self):
        if hasattr(self, '_proc'):
            return self._proc
        else:
            raise Exception("mc server not started.")

    def startMCServer(self):
        self._proc = MCPopen(config()["entry"].split(" "), stdout = PIPE, stdin = PIPE, stderr = STDOUT)
    
    def stopMCServer(self):
        # send command to minecraft server to stop gracefully
        self.proc.stdin.write(b"stop\n")
        self.proc.stdin.flush()
        self.proc.wait()
        print("Stopped minecraft server.")

    @property
    def cmd(self) -> Callable[[str], Any]:
        return self._cmd

    @staticmethod
    def schedule(func: Callable, delay: float, *args, **kwargs) -> SCHEDULE_ID:
        """
        Delay execution of a function
        """
        thread_id = newScheduleID()
        t = ScheduleThread(
            thread_id,
            target = lambda: func(*args, **kwargs), 
            delay = delay
        )
        t.start()
        return thread_id

    @staticmethod
    def randomHexColor() -> str:
        color = "%06x" % random.randint(0, 0xFFFFFF)
        return "#" + color
    
    def _mapColor(self, color: COLOR_T) -> str:
        if color == "random":
            color_ = self.randomHexColor()
        else:
            color_ = color
        return color_

    def title(self, 
              target: Player,
              text: str, 
              ttype: Literal["title", "actionbar"] = "title",
              color: COLOR_T = "white", 
              ):
        self.cmd(f'/title {target.name} {ttype} {{"text": "{text}", "color": "{self._mapColor(color)}"}}')

    def title_setSubtitle(self, 
                    target: Player,
                    text: str, 
                    color: COLOR_T = "white", 
                    ):
        self.cmd(f'/title {target.name} subtitle {{"text": "{text}", "color": "{self._mapColor(color)}"}}')

    def title_setTime(self, 
                        target: Player,
                        times: Tuple[float, float, float] = (10,30,10),  # fadeIn, stay fadeout
                     ):
        """
        times in 0.1 seconds
        """
        self.cmd(f'/title {target.name} times {times[0]} {times[1]} {times[2]}')

    def title_reset(self, target: Player):
        self.cmd(f'/title {target.name} reset')

    def title_clear(self, target: Player):
        self.cmd(f'/title {target.name} clear')

    def tellraw(self, target: Player, text: str, color: COLOR_T = "white"):
        text = text.replace("\n", "\\n").replace('\t', "\\t")
        self.cmd(f'/tellraw {target.name} {{"text": "{text}", "color": "{self._mapColor(color)}"}}')

    def say(self, text: str):
        self.cmd(f"/say {text}")
    
    @property
    def backup_home(self):
        backup_home = os.path.join(config()["server_dir"], "backups")
        if not os.path.exists(backup_home):
            os.mkdir(backup_home)
        return backup_home

    def backupWorld(self, remove_more_than: Optional[int] = None, save_timeout = 10):
        """
        Make a backup of the world
        - remove_more_than: if not None, remove old backups if there are more than this number
        """
        world_dir = os.path.join(config()["server_dir"], config()["world_name"])
        if not os.path.exists(world_dir):
            self.cmd("/say saving faild, world (name:{}) not exists".format(config()["world_name"]))
            return

        __saved_flag = False
        def _backupworld():
            nonlocal __saved_flag
            time_stamp = time.strftime('%Y-%m-%d_%H-%M-%S') 
            new_backup_file = os.path.join(self.backup_home, f"{config()['world_name']}_{time_stamp}.zip")

            # zip the world
            def __pack(directory, zip_filename):
                with zipfile.ZipFile(zip_filename, "w") as zipf:
                    for root, _, files in os.walk(directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, arcname=os.path.relpath(file_path, directory))
            __pack(config()["world_dir"], new_backup_file)


            # make a link of the latest backup
            latest_backup_link = os.path.join(self.backup_home, f"{config()['world_name']}_latest.zip")
            if os.path.exists(latest_backup_link):
                os.remove(latest_backup_link)
            os.symlink(new_backup_file, latest_backup_link)

            # remove old backups if there are too many
            if remove_more_than:
                backups = [ f for f in os.listdir(self.backup_home) if f.startswith(config()["world_name"]) and f.endswith(".zip") ]
                backups.remove(f"{config()['world_name']}_latest.zip")
                backups.sort()
                if len(backups) > remove_more_than:
                    print("removing old backups...")
                    for f in backups[:len(backups)-remove_more_than]:
                        os.remove(os.path.join(self.backup_home, f))
            
            self.cmd("/say Saved to: {}".format(time_stamp))

            # clean up
            self.onWorldSaveCallback = lambda: None
            __saved_flag = True

        def _unloadbackupIfTimeout():
            time.sleep(save_timeout)
            if not __saved_flag:
                self.onWorldSaveCallback = lambda: None
                self.cmd("/say Failed to save due to saving timeout.")
        
        # watch for next saved event (maximum wait for 10s), then do backup:
        self.onWorldSaveCallback = _backupworld
        self.cmd("/save-all flush")
        Thread(target=_unloadbackupIfTimeout, daemon=True)
    
    def listBackups(self) -> list[str]:
        res = [ f[len(config()["world_name"]) + 1:-4] for f in os.listdir(self.backup_home) if f.startswith(config()["world_name"]) and f.endswith('.zip') ]
        res.sort()
        return res
    
    def loadBackup(self, backup_name: str):
        backup_file = os.path.join(self.backup_home, config()["world_name"] + "_" + backup_name + ".zip")
        if not os.path.exists(backup_file):
            raise FileNotFoundError("Backup file not found")
        
        self.stopMCServer()
        world_dir = config()['world_dir']

        shutil.rmtree(world_dir)
        print("Deleted old world")

        with zipfile.ZipFile(backup_file, 'r') as zipref:
            zipref.extractall(path=world_dir)
        print("Extacted backup to ", world_dir)
        
        self.startMCServer()