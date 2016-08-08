from base64 import b64encode

def on_CAP(bot, event):
    if event.arguments[0] == "LS":
        caps = []
        for cap in event.arguments[1].split():
            if cap == "sasl" and bot.config.get("sasl"):
                caps.append(cap)
            elif cap == "account-notify":
                caps.append(cap)
            elif cap == "extended-join":
                caps.append(cap)
            elif cap == "multi-prefix":
                caps.append(cap)
        if len(caps) > 0:
            bot.send("CAP REQ :{0}".format(" ".join(caps)))
        else:
            bot.send("CAP END")
    elif event.arguments[0] == "ACK":
        bot.server["caps"] = event.arguments[1].split()
        if "sasl" not in bot.server["caps"]:
            bot.send("CAP END")
        else:
            bot.send("AUTHENTICATE PLAIN")

def on_AUTHENTICATE(bot, event):
    if event.arguments[0] == "+":
        authstr = b64encode("{0}\x00{0}\x00{1}".format(
            bot.config["username"], bot.config["password"]).encode()).decode()
        bot.send("AUTHENTICATE {0}".format(authstr))

def on_903(bot, event):
    bot.identified = True
    bot.send("CAP END")

def on_904(bot, event):
    bot.log.error("SASL authentication failed")
    bot.quit(die=True)

def on_905(bot, event):
    bot.log.error("SASL authentication aborted.")
    bot.quit(die=True)
