from utils.misc import listreplace

def on_NICK(bot, event):
    nick = event.source.nick
    newnick = event.arguments[0]

    if nick == bot.nick:
        bot.nick = newnick

    if nick in bot.nicks:
        bot.nicks[newnick] = bot.nicks[nick]
        del(bot.nicks[nick])

    for channel in bot.channels:
        if nick in bot.channels[channel]["names"]:
            listreplace(bot.channels[channel]["names"], nick, newnick)

        for prefix in bot.channels[channel]["prefixes"]:
            if nick in bot.channels[channel]["prefixes"][prefix]:
                bot.channels[channel]["prefixes"][prefix].remove(nick))
