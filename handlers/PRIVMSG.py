import threading

def on_PRIVMSG(bot, event):
    msg = event.arguments[0]
    prefix = bot.config["channels"].get(event.target, {}).get("prefix", bot.config["prefix"])
    if ((len(prefix) > 0 and msg.startswith(prefix)) or msg.startswith(bot.nick)
    or event.target == bot.nick):
        bot.log.debug("Possible command: %r", msg)
        if bot.has_flag(event.source, "I"):
            bot.log.debug("Ignoring possible command from %s; user has flag 'I'",
                events.source)
            return
        msg = msg.split(" ", 1)
        if msg[0].startswith(bot.nick):
            if msg[0].rstrip(":,") == bot.nick:
                if len(msg) > 1:
                    msg = msg[1].split(" ", 1)
                else:
                    return
            else:
                return
        plugin = None
        if len(prefix) > 0:
            if msg[0].startswith(prefix):
                msg[0] = msg[0].replace(prefix, "", 1)
        if msg[0] in bot.manager.plugins:
            msg = " ".join(msg).split(" ", 2)
            plugin = msg[0]
            if len(msg) > 1:
                command = msg[1]
                if len(msg) > 2:
                    args = msg[2]
                else:
                    args = ""
            else:
                return
        else:
            command = msg[0]
            if len(msg) > 1:
                args = msg[1]
            else:
                args = ""
        if plugin:
            if plugin in bot.manager.plugins:
                if command in bot.manager.plugins[plugin]["commands"]:
                    for flag in bot.manager.plugins[plugin]["commands"][command]["flags"]:
                        if bot.has_flag(event.source, flag) or flag == "A":
                            bot.log.info("%s called %r in %s", event.source, command,
                                event.target if event.target != bot.nick else "private")
                            t = threading.Thread(
                                target=bot.manager.plugins[plugin]["commands"][command]["func"],
                                args=(bot, event, args))
                            t.daemon = True
                            t.start()
                            break
                    else:
                        bot.log.debug("%s tried to use command %r from plugin %r but "
                            "does not have required flag(s) (%s)", event.source, command,
                            plugin, bot.manager.plugins["commands"][command]["flags"])
                else:
                    bot.log.debug("%s tried to use invalid command %r from plugin %r",
                        event.source, command, plugin)
            else:
                bot.log.debug("%s tried to use command %r from invalid plugin %r",
                    event.source, commmand, plugin)
        else:
            for plugin in bot.manager.plugins.values():
                    if command in plugin["commands"]:
                        for flag in plugin["commands"][command]["flags"]:
                            if bot.has_flag(event.source, flag) or flag == "A":
                                bot.log.info("%s called %r in %s", event.source, command,
                                    event.target if event.target != bot.nick else "private")
                                t = threading.Thread(
                                    target=plugin["commands"][command]["func"],
                                    args=(bot, event, args))
                                t.daemon = True
                                t.start()
                                return
            bot.log.debug("%s tried to use invalid command %r", event.source, command)
