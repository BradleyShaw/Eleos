import copy

def on_KICK(bot, event):
    channel = event.target
    target = event.arguments[0]
    if len(event.arguments) > 1:
        reason = event.arguments[1]
    else:
        reason = ""
    if target == bot.nick:
        bot.log.info("Kicked from {0} by {1} ({2})".format(channel,
            event.source, reason))
        for nick in copy.deepcopy(bot.nicks):
            if channel in bot.nicks[nick]["channels"]:
                bot.nicks[nick]["channels"].remove(channel)
            if len(bot.nicks[nick]["channels"]) == 0:
                del(bot.nicks[nick])
        if channel in bot.channels:
            del(bot.channels[channel])
        if bot.get_channel_config(channel, "autorejoin"):
            bot.log.info("Attempting to re-join {0}".format(channel))
            bot.join(channel, bot.get_channel_config(channel, "key"))

    if channel in bot.channels:
        if target in bot.channels[channel]["names"]:
            bot.channels[channel]["names"].remove(target)
        for prefix in bot.channels[channel]["prefixes"]:
            if target in bot.channels[channel]["prefixes"][prefix]:
                bot.channels[channel]["prefixes"][prefix].remove(target)

    if target in bot.nicks:
        if channel in bot.nicks[target]["channels"]:
            bot.nicks[target]["channels"].remove(channel)
        if len(bot.nicks[target]["channels"]) == 0:
            del(bot.nicks[target])
