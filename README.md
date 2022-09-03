
# Minecraft server control
Run minecraft Java server under Python control

Features:

* Listening to server events and react
* Define your own player commands
* Broadcast server log via webpage

The realization is achieved by watching server log and send server command using inter-process communication.

## Usage

To start, run:
```
python .
```
On the first run, the program will create a configuration file at: `mcservercontrol/config.json`.   
Edit the configuation file and run the above command again will start the server.

### Configure
The configuation file is as follows:
```
{
    // Where your server.jar resides
    "server_dir": "/directory/of/the/minecraft/server",

    // Command to start the server
    "entry": "java -Xmx1024M -Xms1024M -jar server.jar nogui",

    // World name, for backing-up the world
    "world_name": "world",

    // The server log will be broadcast to http://localhost:<port>/info/log
    "broadcast_port": 25566
}
```

## Development

The implementation is completely object-oriented and pretty much typed, thus should be friendly to use.  
You can define your own logic with the APIs.

You would basically like to inherite from `observer.PlayerObserver` and `observer.PlayerCommandObserver`, then register them to the minecraft server listener:

* `PlayerObserver` is used to watch player behaviour then react to that
* `PlayerCommandObserver` is a subclass of `PlayerObserver`, defferent lies in that it is used to implement your own player commands. All user-defined player commands should start with backslash(`\`), e.g. `\help`

For API useage, see `demo.py`

---
## New to Minecraft server hosting?
Some useful resources:

* [Minecraft wiki - Tutorials/Setting up a server ](https://minecraft.fandom.com/wiki/Tutorials/Setting_up_a_server)  
* [Minecraft wiki - Commands](https://minecraft.fandom.com/wiki/Commands)
