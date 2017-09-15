import time

import utils.task as task


def on_001(bot, event):
    bot.connected = True
    if 'umodes' in bot.config:
        bot.mode(bot.nick, bot.config['umodes'])
    if bot.identified:
        bot.autojoin()
    else:
        bot.msg('NickServ', 'IDENTIFY {0} {1}'.format(
            bot.config['username'], bot.config['password']))
    if bot.nick != bot.config['nick'] and 'password' in bot.config:
        bot.msg('NickServ', 'REGAIN {0} {1}'.format(
            bot.config['nick'], bot.config['password']))
    bot.lastping = time.time()
    bot.pingtask = task.run_every(30, bot.ping)
    bot.stickytask = task.run_every(10, bot.sticky)


def on_433(bot, event):
    if not bot.connected:
        bot.nick += '_'
        bot.send('NICK {0}'.format(bot.nick))


def on_437(bot, event):
    if not bot.connected:
        bot.nick += '_'
        bot.send('NICK {0}'.format(bot.nick))


def on_474(bot, event):
    channel = event.arguments[0]
    bot.msg('ChanServ', 'UNBAN {0}'.format(channel))


def on_473(bot, event):
    channel = event.arguments[0]
    bot.msg('ChanServ', 'INVITE {0}'.format(channel))
