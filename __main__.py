from src.listener import EventListener
from src.server import Server
from src.observer import getDefaultObservers


if __name__ == "__main__":
    listener = EventListener()
    listener.startMCServer()
    server = Server(listener.cmd_interface)

    # load predefined observers
    listener.register(*getDefaultObservers(server))

    # ======================== Your custom code here =====================
    from demo import WelcomeObserver, GoodbyeObserver, CommandSuicide, CommandOnlineTime

    # Add custom observers
    obs = [
        WelcomeObserver(server),
        GoodbyeObserver(server),
        CommandSuicide("suicide", server),
        CommandOnlineTime("online-time", server)
    ]

    # register them to the listener
    listener.register(*obs)

    # Add another callable observer (with __call__), and register it to be run in daemon loop
    from demo import RemindAddictionCallback
    listener.daemon.setObserveInterval(1)       # Maybe change daemon's looping interval
    remind_addiction_ob = RemindAddictionCallback(server)
    listener.addDaemonCallback(remind_addiction_ob)

    # register to the listener
    listener.register(remind_addiction_ob)

    # ======================== Custom code ends =========================


    listener.listen()
