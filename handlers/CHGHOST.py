def on_396(bot, event):
    nick = bot.nick
    newhost = event.arguments[0]
    if nick in bot.nicks:
        bot.nicks[nick]['host'] = newhost
