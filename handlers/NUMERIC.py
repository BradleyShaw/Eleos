import threading
import time

def on_001(bot, event):
    autojoins = []
    if bot.identified:
        for channel, conf in bot.config["channels"].items():
            if conf.get("autojoin", bot.config.get("autojoin")):
                if conf.get("key"):
                    autojoins.append(" ".join([channel, conf["key"]]))
                else:
                    autojoins.append(channel)
        if len(autojoins) > 0:
            bot.multijoin(autojoins)
    else:
        bot.msg("NickServ", "IDENTIFY {0} {1}".format(
            bot.config["username"], bot.config["password"]))
    if bot.nick != bot.config["nick"]:
        bot.msg("NickServ", "REGAIN {0} {1}".format(
            bot.config["nick"], bot.config["password"]))
    bot.lastping = time.time()
    if not bot.pingthread:
        bot.pingthread = threading.Thread(target=bot.pingtimer)
        bot.pingthread.daemon = True
        bot.pingthread.start()
