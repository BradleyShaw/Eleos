def on_NOTICE(bot, event):
    msg = event.arguments[0]
    if event.source.nick == "NickServ":
        if (not bot.identified and
            msg.startswith("You are now identified")):
            autojoins = []
            for channel, conf in bot.config["channels"].items():
                if conf.get("autojoin", bot.config.get("autojoin")):
                    if conf.get("key"):
                        autojoins.append(" ".join([channel, conf["key"]]))
                    else:
                        autojoins.append(channel)
                if len(autojoins) > 0:
                    bot.multijoin(autojoins)
    elif event.source.nick == "ChanServ":
        if msg.startswith("You are not authorized to (de)op"):
            msg = msg.split(" ")
            nick = msg[6].strip("\x02")
            channel = msg[8].strip("\x02")
            if nick == bot.nick and channel in bot.opqueue:
                bot.opqueue[channel].put(False)
        elif msg.endswith("is not registered."):
            channel = msg.split(" ")[1].strip("\x02")
            if channel in bot.opqueue:
                bot.opqueue[channel].put(False)
        elif msg.startswith("Unbanned \x02{0}\x02 on".format(bot.nick)):
            channel = msg.split(" ")[3].strip("\x02")
            if bot.get_channel_config(channel, "autorejoin"):
                bot.join(channel, bot.get_channel_config(channel, "key"))
