from utils.irc import List

def on_352(bot, event): # WHO
    nick = event.arguments[4]
    user = event.arguments[1]
    host = event.arguments[2]
    realname = event.arguments[6].replace("0 ", "", 1)
    channel = event.arguments[0]
    status = event.arguments[5]
    if nick not in bot.nicks:
        bot.nicks[nick] = {}
        bot.nicks[nick]["channels"] = List()
    bot.nicks[nick]["user"] = user
    bot.nicks[nick]["host"] = host
    bot.nicks[nick]["realname"] = realname
    bot.nicks[nick]["account"] = None # WHO replies don't contain the account
    bot.nicks[nick]["ip"] = None
    bot.nicks[nick]["away"] = None
    if channel != "*":
        if channel not in bot.nicks[nick]["channels"]:
            bot.nicks[nick]["channels"].append(channel)
        for char in status:
            if char not in bot.server["prefixes"]:
                continue
            if nick not in bot.channels[channel]["prefixes"][char]:
                bot.channels[channel]["prefixes"][char].append(nick)
    bot.whois(nick)

def on_354(bot, event): # WHOX
    magic = event.arguments[0]
    # WHOX can have different parameters, so
    # if the reply doesn't have our magic number
    # then let's ignore it to avoid IndexError later
    if magic != "158":
        return
    channel = event.arguments[1]
    user = event.arguments[2]
    ipaddr = event.arguments[3]
    host = event.arguments[4]
    nick = event.arguments[5]
    status = event.arguments[6]
    account = event.arguments[7]
    realname = event.arguments[8]
    if nick not in bot.nicks:
        bot.nicks[nick] = {}
        bot.nicks[nick]["channels"] = List()
    bot.nicks[nick]["user"] = user
    bot.nicks[nick]["host"] = host
    bot.nicks[nick]["realname"] = realname
    bot.nicks[nick]["account"] = account if account != "0" else None
    bot.nicks[nick]["ip"] = ipaddr if ipaddr != "255.255.255.255" else None
    bot.nicks[nick]["away"] = None
    if status.startswith("G"):
        bot.whois(nick)
    if channel != "*":
        if channel not in bot.nicks[nick]["channels"]:
            bot.nicks[nick]["channels"].append(channel)
        for char in status:
            if char not in bot.server["prefixes"]:
                continue
            if nick not in bot.channels[channel]["prefixes"][char]:
                bot.channels[channel]["prefixes"][char].append(nick)
