def on_NICK(bot, event):
    if event.source.nick == bot.nick:
        bot.nick = event.arguments[0]
