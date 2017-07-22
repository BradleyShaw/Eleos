def on_INVITE(bot, event):
    if bot.has_flag(event.source, 'o', channel=event.arguments[0]):
        bot.join(event.arguments[0])
