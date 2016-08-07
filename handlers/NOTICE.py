def on_NOTICE(bot, event):
    if event.source.nick == "NickServ":
        if (not bot.identified and
            event.arguments[0].startswith("You are now identified")):
            autojoins = []
            for channel, conf in bot.config["channels"].items():
                if conf.get("autojoin", bot.config.get("autojoin")):
                    if conf.get("key"):
                        autojoins.append(" ".join([channel, conf["key"]]))
                    else:
                        autojoins.append(channel)
                if len(autojoins) > 0:
                    bot.multijoin(autojoins)
