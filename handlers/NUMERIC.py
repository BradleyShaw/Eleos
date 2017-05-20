import threading
import time

import utils.task as task

def on_001(bot, event):
    autojoins = []
    keys = []
    bot.connected = True
    if "umodes" in bot.config:
        bot.mode(bot.nick, bot.config["umodes"])
    if bot.identified:
        for channel in bot.config["channels"]:
            if channel == "default":
                continue
            if bot.get_channel_config(channel, "autojoin"):
                autojoins.append(channel)
                key = bot.get_channel_config(channel, "key")
                if key:
                    keys.append(key)
        if len(autojoins) > 0:
            bot.multijoin(autojoins, keys)
    else:
        bot.msg("NickServ", "IDENTIFY {0} {1}".format(
            bot.config["username"], bot.config["password"]))
    if bot.nick != bot.config["nick"] and "password" in bot.config:
        bot.msg("NickServ", "REGAIN {0} {1}".format(
            bot.config["nick"], bot.config["password"]))
    bot.lastping = time.time()
    bot.pingtask = task.run_every(30, bot.ping)

def on_433(bot, event):
    if not bot.connected:
        bot.nick += "_"
        bot.send("NICK {0}".format(bot.nick))

def on_437(bot, event):
    if not bot.connected:
        bot.nick += "_"
        bot.send("NICK {0}".format(bot.nick))

def on_474(bot, event):
    channel = event.arguments[0]
    if bot.get_channel_config(channel, "autorejoin"):
        bot.msg("ChanServ", "UNBAN {0}".format(channel))
