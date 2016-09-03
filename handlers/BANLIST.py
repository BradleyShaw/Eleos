from utils.irc import List

def on_367(bot, event):
    channel = event.arguments[0]
    mask = event.arguments[1]
    if not bot.channels[channel]["syncing"]["banlist"]:
        bot.channels[channel]["bans"] = List()
        bot.channels[channel]["syncing"]["banlist"] = True
    if mask not in bot.channels[channel]["bans"]:
        bot.channels[channel]["bans"].append(mask)

def on_368(bot, event):
    channel = event.arguments[0]
    bot.channels[channel]["syncing"]["banlist"] = False

def on_728(bot, event):
    channel = event.arguments[0]
    mask = event.arguments[2]
    if not bot.channels[channel]["syncing"]["quietlist"]:
        bot.channels[channel]["quiets"] = List()
        bot.channels[channel]["syncing"]["quietlist"] = True
    if mask not in bot.channels[channel]["quiets"]:
        bot.channels[channel]["quiets"].append(mask)

def on_729(bot, event):
    channel = event.arguments[0]
    bot.channels[channel]["syncing"]["quietlist"] = False
