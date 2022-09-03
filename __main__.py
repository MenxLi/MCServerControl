from mcservercontrol import EventListener, getDefaultObservers


if __name__ == "__main__":
    # Have to start the minecraft server before initialize observers
    listener = EventListener()
    listener.startServer()

    # Load predefined observers
    listener.register(*getDefaultObservers())

    # ======================== Your custom code here =====================
    from demo import WelcomeObserver, GoodbyeObserver, CommandSuicide, CommandOnlineTime

    # Add custom observers
    obs = [
        WelcomeObserver(),
        GoodbyeObserver(),
        CommandSuicide("suicide"),
        CommandOnlineTime("online-time")
    ]

    # register them to the listener
    listener.register(*obs)

    # Add another callable observer (with __call__), and register it to be run in daemon loop
    from demo import RemindAddictionCallback

    listener.daemon.setObserveInterval(1)       # Maybe change daemon's looping interval
    remind_addiction_ob = RemindAddictionCallback()
    listener.addDaemonCallback(remind_addiction_ob)

    # register to the listener
    listener.register(remind_addiction_ob)

    # ======================== Custom code ends =========================

    # Start listening loop
    listener.listen()
