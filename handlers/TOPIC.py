def on_331(bot, event):
    channel = event.arguments[0]
    bot.channels[channel]["topic"] = None

def on_332(bot, event):
    channel = event.arguments[0]
    topic = event.arguments[1]
    bot.channels[channel]["topic"] = topic

def on_TOPIC(bot, event):
    channel = event.arguments[0]
    topic = event.arguments[1]
    if len(topic) > 0:
        bot.channels[channel]["topic"] = topic
    else:
        bot.channels[channel]["topic"] = None
