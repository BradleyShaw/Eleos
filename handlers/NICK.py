from utils.misc import listreplace

def on_NICK(bot, event):
    nick = event.source.nick
    newnick = event.target

    if nick == bot.nick:
        bot.nick = newnick

    if nick in bot.nicks:
        bot.nicks[newnick] = bot.nicks[nick]
        del(bot.nicks[nick])

    for channel in bot.channels:
        if nick in bot.channels[channel]["names"]:
            listreplace(bot.channels[channel]["names"], nick, newnick)

        if nick in bot.channels[channel]["ops"]:
            listreplace(bot.channels[channel]["ops"], nick, newnick)

        if nick in bot.channels[channel]["voices"]:
            listreplace(bot.channels[channel]["voices"], nick, newnick)
