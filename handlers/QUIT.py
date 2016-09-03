def on_QUIT(bot, event):
    nick = event.source.nick

    if nick in bot.nicks:
        del(bot.nicks[nick])

    for channel in bot.channels:
        if nick in bot.channels[channel]["names"]:
            bot.channels[channel]["names"].remove(nick)

        if nick in bot.channels[channel]["ops"]:
            bot.channels[channel]["ops"].remove(nick)

        if nick in bot.channels[channel]["voices"]:
            bot.channels[channel]["voices"].remove(nick)
