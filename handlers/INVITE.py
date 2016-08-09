def on_INVITE(bot, event):
    if bot.has_flag(event.source, "a"):
        bot.join(event.arguments[0])
