from collections.abc import Callable
from typing import IO
import os, signal, time
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from .serverLogParser import parseLine

WORKING_DIR = "./_server"

# Command to start the server
ENTRY = "java -Xmx1024M -Xms1024M -jar server.jar nogui "      # no excaping space

class MCPopen(Popen):
    # Type checking purpose
    stdin: IO[bytes]
    stdout: IO[bytes]

class InputThread(Thread):
    def __init__(self, mc_proc: MCPopen) -> None:
        """
         - mc_proc: minecraft server process
        """
        # daemon thread will end when main thread exit
        super().__init__(daemon=True)
        self._mc_proc = mc_proc

    @property
    def mc_proc(self):
        return self._mc_proc

    def run(self):
        while True:
            _usr_input = input()
            self.onInput(_usr_input)

    def onInput(self, x: str):
        self._sendServerCommand(x)

    def _sendServerCommand(self, x: str):
        if not x.endswith("\n"):
            x += "\n"
        self.mc_proc.stdin.write(x.encode("utf-8"))
        self.mc_proc.stdin.flush()

def schedule(func: Callable, delay: float, *args, **kwargs):
    """
    Delay execution of an function
    """
    def _f():
        time.sleep(delay)
        func(*args, **kwargs)
    Thread(target = func, args=(), daemon = True).start()

def main():
    os.chdir(WORKING_DIR)

    proc = MCPopen(ENTRY.split(" "), stdout = PIPE, stdin = PIPE, stderr = STDOUT)

    # Start a thread that listen to user input
    input_thread = InputThread(proc)
    input_thread.start()

    # Catch KeyboardInterruption
    def handler(signum, frame):
        nonlocal proc
        print("Stopping gracefully...")
        # send command to minecraft server to stop gracefully
        proc.stdin.write(b"stop\n")
        proc.stdin.flush()
    # Handle interrupt signal
    signal.signal(signal.SIGINT, handler)

    while proc.poll() is None:
        # Handler
        handleIOLoop(proc.stdin, proc.stdout, input_thread.onInput)

    proc.stdout.close()
    proc.stdin.close()
    exit(proc.poll())

def handleIOLoop(stdin: IO[bytes], stdout: IO[bytes], cmd: Callable):
    """
    Implement some reaction based on server stdout
     - stdin: server stdin
     - stdout: server stdout
    """


    output = stdout.readline()
    if output:
        line = output.decode("utf-8")
        ev = parseLine(line)
        print(ev["log_line"], end = "")

        if ev["etype"] == "login":
            user_name = ev["user_name"]
            def sayWelcome():
                cmd("/title {} title {}".format(
                    user_name, '{"text": "Welcome"}'
                ))
                cmd("/list")
            schedule(sayWelcome, 3)

        if ev["etype"] == "listplayer":
            all_players = ev["all_players"]
            cmd(f"/say Now online:{all_players}")

        if ev["etype"] == "cmd":
            user_name = ev["user_name"]
            if ev["cmd"] =="\\suicide\n":
                cmd(f"/kill {user_name}")



if __name__ == "__main__":
    main()
