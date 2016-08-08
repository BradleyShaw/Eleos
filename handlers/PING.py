import time

def on_PING(bot, event):
    bot.send("PONG :{0}".format(event.arguments[0]))

def on_PONG(bot, event):
    bot.lastping = time.time()
