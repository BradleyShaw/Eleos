import re

import utils.threads as threads


def on_PRIVMSG(bot, event):
    if bot.has_flag(event.source, "I"):
        bot.log.debug("Ignoring message from %s", event.source)
        return
    msg = event.arguments[0]
    for plugin in bot.manager.plugins.values():
        for regex, cfg in plugin["regexes"].items():
            matches = re.findall(regex, msg)
            if matches:
                threads.run(cfg["func"], bot, event, matches)
    prefix = bot.get_channel_config(event.target, "prefix")
    if ((len(prefix) > 0 and msg.startswith(prefix)) or
            msg.startswith(bot.nick) or event.target == bot.nick):
        bot.log.debug("Possible command: %r", msg)
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
        command = msg[0]
        if len(msg) > 1:
            args = msg[1]
            if msg[0] in bot.manager.plugins:
                msg = " ".join(msg).split(" ", 2)
                if len(msg) > 1:
                    if msg[1] in bot.manager.plugins[msg[0]]["commands"]:
                        command = msg[1]
                        if len(msg) > 2:
                            args = msg[2]
                        else:
                            args = ""
        else:
            args = ""
        if plugin:
            if plugin in bot.manager.plugins:
                if command in bot.manager.plugins[plugin]["commands"]:
                    data = bot.manager.plugins[plugin]
                    global_only = data["commands"][command]["perms"]["global"]
                    flags = data["commands"][command]["perms"]["flags"]
                    channel = (event.target if bot.is_channel(event.target)
                               else None)
                    target = (event.target if event.target != bot.nick else
                              "private")
                    for flag in flags:
                        if (bot.has_flag(event.source, flag, global_only,
                                         channel) or flag == "A"):
                            bot.log.info("%s called %r in %s", event.source,
                                         command, target)
                            threads.run(data["commands"][command]["func"], bot,
                                        event, args)
                            break
                    else:
                        bot.log.debug("%s tried to use command %r from plugin "
                                      "%r but does not have required flag(s) "
                                      "(%s)", event.source, command, plugin,
                                      flags)
                        bot.reply(event, "Error: You are not authorized to "
                                  "perform this command.")
                else:
                    bot.log.debug("%s tried to use invalid command %r from "
                                  "plugin %r", event.source, command, plugin)
            else:
                bot.log.debug("%s tried to use command %r from invalid plugin "
                              "%r", event.source, command, plugin)
        else:
            for plugin in bot.manager.plugins.values():
                    if command in plugin["commands"]:
                        data = plugin["commands"][command]
                        global_only = data["perms"]["global"]
                        flags = data["perms"]["flags"]
                        channel = (event.target if bot.is_channel(event.target)
                                   else None)
                        target = (event.target if event.target != bot.nick else
                                  "private")
                        for flag in flags:
                            if (bot.has_flag(event.source, flag, global_only,
                                             channel) or flag == "A"):
                                bot.log.info("%s called %r in %s",
                                             event.source, command, target)
                                threads.run(
                                    plugin["commands"][command]["func"], bot,
                                    event, args)
                                return
                        bot.log.debug("%s tried to use command %r but does "
                                      "not have required flag(s) (%s)",
                                      event.source, command, flags)
                        bot.reply(event, "Error: You are not authorized to "
                                  "perform this command.")
                        return
            factoids = bot.get_channel_factoids(event.target)
            if command in factoids:
                factoid = factoids[command]
                args = args.strip(" ").split(" ")
                target = (event.target if event.target != bot.nick else
                          'private')
                if len(args) > 0:
                    if args[0] in bot.nicks:
                        factoid = "{0}: {1}".format(args[0], factoid)
                bot.log.info("%s called %r in %s", event.source, command,
                             target)
                bot.reply(event, factoid)
                return
            bot.log.debug("%s tried to use invalid command %r", event.source,
                          command)
