from mcservercontrol import EventListener, getDefaultObservers


if __name__ == "__main__":
    # Have to start the minecraft server before initialize observers
    listener = EventListener()
    listener.startServer()

    # Load default observers
    listener.register(*getDefaultObservers())

    # ======================== Your custom code here =====================
    from demo import WelcomeObserver, CommandSuicide

    # Add custom observers
    obs = [
        WelcomeObserver(),
        CommandSuicide("suicide"),
    ]

    # register them to the listener
    listener.register(*obs)

    # ======================== Custom code ends =========================

    # Optionally load some more predefined observers
    from mcservercontrol.addons import GoodbyeObserver, CommandKillItem
    from mcservercontrol.addons.onlineControl import CommandOnlineTime, RemindAddictionCallback

    obs = [
        GoodbyeObserver(),
        CommandOnlineTime("online-time"),
        CommandKillItem("kill-item"),
    ]

    # register them to the listener
    listener.register(*obs)

    # Add another callable observer (with __call__), and register it to be run in daemon loop
    listener.daemon.setObserveInterval(1)       # Maybe change daemon's looping interval
    remind_addiction_ob = RemindAddictionCallback()
    listener.addDaemonCallback(remind_addiction_ob)

    # register to the listener
    listener.register(remind_addiction_ob)

    # Start listening loop
    listener.listen()
