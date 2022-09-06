from mcservercontrol.player import Player

player = Player("Monsoon", {"is_online": True})
print(player.status)
print(player.status.is_online)

ok = player.status.setdefault("ok_status", "ok")
print(player.status.has("ok_status"))
print(ok)
#  print(player.status.notok_status)
