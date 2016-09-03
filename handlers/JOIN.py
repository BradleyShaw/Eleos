from utils.irc import List

def on_JOIN(bot, event):
    nick = event.source.nick
    channel = event.target
    if nick == bot.nick:
        bot.log.debug("Joined to %s", channel)
        if channel not in bot.channels:
            bot.channels[channel] = {}
        bot.channels[channel]["topic"] = ""
        bot.channels[channel]["names"] = List()
        bot.channels[channel]["bans"] = List()
        bot.channels[channel]["quiets"] = List()
        bot.channels[channel]["ops"] = List()
        bot.channels[channel]["voices"] = List()
        bot.channels[channel]["syncing"] = {
            "names": False,
            "banlist": False,
            "quietlist": False
        }
        bot.log.debug("Syncing users for %s", channel)
        bot.who(channel)
        bot.log.debug("Syncing bans and quiets for %s", channel)
        bot.mode(channel, "bq")
    if nick not in bot.channels[channel]["names"]:
        bot.channels[channel]["names"].append(nick)
    if nick not in bot.nicks:
        bot.nicks[nick] = {}
        bot.nicks[nick]["channels"] = List()
    bot.nicks[nick]["user"] = event.source.user
    bot.nicks[nick]["host"] = event.source.host
    if "account" not in bot.nicks[nick]:
        bot.nicks[nick]["account"] = None
    if "realname" not in bot.nicks[nick]:
        bot.nicks[nick]["realname"] = None
    if "extended-join" in bot.server["caps"]:
        if event.arguments[0] != "*":
            bot.nicks[nick]["account"] = event.arguments[0]
        bot.nicks[nick]["realname"] = event.arguments[1]
    if channel not in bot.nicks[nick]["channels"]:
        bot.nicks[nick]["channels"].append(channel)
