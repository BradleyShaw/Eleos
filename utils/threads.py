from threading import Thread
import sys


def log_errors(func, bot, *args, **kwargs):
    try:
        func(bot, *args, **kwargs)
    except Exception:
        bot.log.debug('Error:', exc_info=sys.exc_info())


def run(func, bot, *args, **kwargs):
    args = (func, bot) + args
    t = Thread(target=log_errors, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
    return t
