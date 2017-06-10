def on_311(bot, event):
    nick = event.arguments[0]
    user = event.arguments[1]
    host = event.arguments[2]
    gecos = event.arguments[4]
    if nick in bot.nicks:
        bot.nicks[nick]["user"] = user
        bot.nicks[nick]["host"] = host
        bot.nicks[nick]["realname"] = gecos


def on_330(bot, event):
    nick = event.arguments[0]
    account = event.arguments[1]
    if nick in bot.nicks:
        bot.nicks[nick]["account"] = account


def on_338(bot, event):
    nick = event.arguments[0]
    ipaddr = event.arguments[1]
    if nick in bot.nicks:
        bot.nicks[nick]["ip"] = ipaddr
