from utils.irc import List


def on_353(bot, event):
    channel = event.arguments[1]
    names = event.arguments[2]
    if not bot.channels[channel]['syncing']['names']:
        bot.channels[channel]['names'] = List()
        bot.channels[channel]['syncing']['names'] = True
    for nick in names.split():
        nick = nick.lstrip(''.join(list(
                           bot.server['ISUPPORT']['PREFIX'].values())))
        if nick not in bot.channels[channel]['names']:
            bot.channels[channel]['names'].append(nick)


def on_366(bot, event):
    channel = event.arguments[0]
    bot.channels[channel]['syncing']['names'] = False
