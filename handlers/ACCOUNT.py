def on_ACCOUNT(bot, event):
    nick = event.source.nick
    account = event.target
    if account != '*':
        bot.nicks[nick]['account'] = account
    else:
        bot.nicks[nick]['account'] = None
