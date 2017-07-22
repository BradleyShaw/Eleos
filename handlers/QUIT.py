def on_QUIT(bot, event):
    nick = event.source.nick

    if nick in bot.nicks:
        del(bot.nicks[nick])

    for channel in bot.channels:
        if nick in bot.channels[channel]['names']:
            bot.channels[channel]['names'].remove(nick)

        for prefix in bot.channels[channel]['prefixes']:
            if nick in bot.channels[channel]['prefixes'][prefix]:
                bot.channels[channel]['prefixes'][prefix].remove(nick)
