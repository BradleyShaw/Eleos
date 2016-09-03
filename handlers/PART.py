import copy

def on_PART(bot, event):
    nick = event.source.nick
    channel = event.target
    if len(event.arguments) > 0:
        reason = event.arguments[0]
    else:
        reason = ""

    if nick == bot.nick:
        for user in copy.deepcopy(bot.nicks):
            if channel in bot.nicks[user]["channels"]:
                bot.nicks[user]["channels"].remove(channel)
            if len(bot.nicks[user]["channels"]) == 0:
                del(bot.nicks[user])
        if channel in bot.channels:
            del(bot.channels[channel])
        if reason.startswith("requested by"):
            bot.log.info("removed from {0}".format(channel))
            if bot.config["channels"].get(channel, {}).get("autorejoin",
                bot.config.get("autorejoin"))
                bot.log.info("Attempting to re-join {0}".format(channel))
                bot.join(channel, bot.config["channels"].get(channel, {}).get("key"))

    if channel in bot.channels:
        if nick in bot.channels[channel]["names"]:
            bot.channels[channel]["names"].remove(nick)
        if nick in bot.channels[channel]["ops"]:
            bot.channels[channel]["ops"].remove(nick)
        if nick in bot.channels[channel]["voices"]:
            bot.channels[channel]["voices"].remove(nick)

    if nick in bot.nicks:
        if channel in bot.nicks[nick]["channels"]:
            bot.nicks[nick]["channels"].remove(channel)
        if len(bot.nicks[nick]["channels"]) == 0:
            del(bot.nicks[nick])
