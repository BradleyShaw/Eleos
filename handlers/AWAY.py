def on_AWAY(bot, event):
    nick = event.source.nick
    if len(event.arguments) > 0:
        awaymsg = event.arguments[0]
    else:
        awaymsg = None
    if nick in bot.nicks:
        bot.nicks[nick]["away"] = awaymsg
