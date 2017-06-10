from utils.exceptions import CleanExit


def on_ERROR(bot, event):
    if bot.dying:
        raise CleanExit
    else:
        bot.reconnect()
