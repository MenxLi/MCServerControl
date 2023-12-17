
# Minecraft server control
Run minecraft-Java server under Python control

Features:

* Listen to server events and react
* Define your own player commands
* Broadcast server log via webpage

The realization is achieved by watching server log and send server command using inter-process communication.

## Usage

### Installation
```sh
pip install .
```
### Usage
To start, go to the directory where you want to put the script files (typically java server directory), run:
```sh
mcservercontrol init
```
On the first run, the program will create a configuration file at: `{working_directory}/mcservercontrol.json`.   
Edit the configuation file and start the server with:
```sh
python .
```

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

The implementation is object-oriented and strongly typed, making it friendly and easy to use.  
You can define your own logic with the APIs.

To get started, you can inherite from `observer.PlayerObserver` and `observer.PlayerCommandObserver`, then register them to the minecraft server listener:

- `PlayerObserver` class allows you to monitor player behavior and react to it
- `PlayerCommandObserver` is a subclass of `PlayerObserver`, defference lies in that it is used to implement your own player commands. All user-defined player commands should start with backslash(`\`), e.g. `\help`

For API useage, see `mcservercontrol.addons` and `__main__.py` generated via initialization.

---
## New to Minecraft server hosting?
Some useful resources:

* [Minecraft wiki - Tutorials/Setting up a server ](https://minecraft.fandom.com/wiki/Tutorials/Setting_up_a_server)  
* [Minecraft wiki - Commands](https://minecraft.fandom.com/wiki/Commands)