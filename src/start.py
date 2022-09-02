from typing import IO, Callable, Any
import os, signal, time, random
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from multiprocessing import Process, Queue
from .configReader import WORKING_DIR, ENTRY, BROADCAST_PORT
from .serverLogParser import parseLine
from .broadcastServer import startServer as startBroadcastServer
from .actions import ServerActions


class MCPopen(Popen):
    # Type checking purpose
    stdin: IO[bytes]
    stdout: IO[bytes]

class InputThread(Thread):
    """
    Thread listening to user input from console
    """
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

def main():
    os.chdir(WORKING_DIR)

    proc = MCPopen(ENTRY.split(" "), stdout = PIPE, stdin = PIPE, stderr = STDOUT)

    # Start a thread that listen to user input
    input_thread = InputThread(proc)
    input_thread.start()

    # Start broadcast server process
    event_queue = Queue()
    broadcast_proc = Process(target=startBroadcastServer, args = (BROADCAST_PORT, event_queue))
    broadcast_proc.start()

    # Catch KeyboardInterruption
    def handler(signum, frame):
        nonlocal proc
        print("Stopping gracefully...")
        # send command to minecraft server to stop gracefully
        proc.stdin.write(b"stop\n")
        proc.stdin.flush()
        broadcast_proc.join()
    # Handle interrupt signal
    signal.signal(signal.SIGINT, handler)

    while proc.poll() is None:
        # Log listening loop
        server_act = ServerActions(input_thread.onInput)
        handleIOLoop(proc.stdin, proc.stdout, server_act, input_thread.onInput, event_queue)

    proc.stdout.close()
    proc.stdin.close()
    exit(proc.poll())

def handleIOLoop(stdin: IO[bytes], stdout: IO[bytes], server_act: ServerActions, cmd_input: Callable[[str], Any], event_queue: Queue):
    """
    Implement some reaction based on server stdout
     - stdin: server stdin
     - stdout: server stdout
     - cmd: method to trigger a custom command
     - event_queue: queue to put event dict for inter-process communication
    """
    output = stdout.readline()
    if not output:
        return


    line = output.decode("utf-8")
    ev = parseLine(line)

    # print server log to console
    print(ev["log_line"], end = "")

    # broadcast event to other processes
    event_queue.put(ev)

    # Implement reactions based on event type ⬇

    if ev["etype"] == "listplayer":
        all_players = ev["all_players"]
        # tell every one who is online when listing players
        cmd_input(f"/say Now online:{all_players}")

    if ev["etype"] == "login":
        user_name = ev["user_name"]
        # Welcome and list players when a user login
        server_act.action_sayHello(user_name)

    # custom commands (starts with "\")
    if ev["etype"] == "cmd":
        user_name = ev["user_name"]
        if ev["cmd"][0] =="suicide":
            server_act.action_killPlayer(user_name)

if __name__ == "__main__":
    main()
