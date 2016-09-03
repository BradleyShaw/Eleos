import threading
import time

def on_001(bot, event):
    autojoins = []
    keys = []
    bot.connected = True
    if bot.identified:
        for channel, conf in bot.config["channels"].items():
            if conf.get("autojoin", bot.config.get("autojoin")):
                autojoins.append(channel)
                if conf.get("key"):
                    keys.append(conf["key"])
        if len(autojoins) > 0:
            bot.multijoin(autojoins, keys)
    else:
        bot.msg("NickServ", "IDENTIFY {0} {1}".format(
            bot.config["username"], bot.config["password"]))
    if bot.nick != bot.config["nick"] and "password" in bot.config:
        bot.msg("NickServ", "REGAIN {0} {1}".format(
            bot.config["nick"], bot.config["password"]))
    bot.lastping = time.time()
    if not bot.pingthread:
        bot.pingthread = threading.Thread(target=bot.pingtimer)
        bot.pingthread.daemon = True
        bot.pingthread.start()

def on_433(bot, event):
    if not bot.connected:
        bot.nick += "_"
        bot.send("NICK {0}".format(bot.nick))

def on_437(bot, event):
    if not bot.connected:
        bot.nick += "_"
        bot.send("NICK {0}".format(bot.nick))
