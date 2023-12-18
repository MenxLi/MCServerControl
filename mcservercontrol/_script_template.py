from mcservercontrol import EventListener, getDefaultObservers


if __name__ == "__main__":
    # Have to start the minecraft server before initialize observers
    listener = EventListener()
    listener.startServer()

    # Load default observers
    listener.register(*getDefaultObservers())

    # Load some more predefined observers
    from mcservercontrol.addons import WelcomeObserver, GoodbyeObserver, CommandSuicide
    from mcservercontrol.addons.onlineControl import CommandOnlineTime
    from mcservercontrol.addons.killItem import CommandKillItem
    from mcservercontrol.addons.teleportPlayer import CommandTeleportPlayer
    from mcservercontrol.addons.save import CommandBackup
    obs = [
        WelcomeObserver(),
        GoodbyeObserver(),
        CommandSuicide("suicide"),
        CommandOnlineTime("online-time", alias=["ot"]),
        CommandKillItem("kill-item", alias=["ki"]),
        CommandTeleportPlayer("teleport-player", alias=["tpp"]),
        CommandBackup("backup"),
    ]
    # register them to the listener
    listener.register(*obs)

    # Add another callable observer (with __call__), and register it to be run in daemon loop
    from mcservercontrol.addons.onlineControl import RemindAddictionCallback
    listener.daemon.setObserveInterval(1)       # Maybe change daemon's looping interval
    remind_addiction_ob = RemindAddictionCallback()
    listener.addDaemonCallback(remind_addiction_ob)
    # register to the listener
    listener.register(remind_addiction_ob)

    #  =========== May register more custom listener here ===========
    # Please refer to above examples for the implementation and usage
    # ...
    # ===============================================================

    # Start listening loop
    listener.listen()
