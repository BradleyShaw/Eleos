from utils.irc import List
import utils.misc as misc
import copy

def on_MODE(bot, event):
    if bot.is_channel(event.target):
        channel = event.target
        modes = bot.split_modes(event.arguments)
        for mode in modes:
            if mode.startswith("+b"):
                mask = mode.split()[1]
                if mask not in bot.channels[channel]["bans"]:
                    bot.channels[channel]["bans"].append(mask)
            elif mode.startswith("-b"):
                mask = mode.split()[1]
                if mask in bot.channels[channel]["bans"]:
                    bot.channels[channel]["bans"].remove(mask)
            elif mode.startswith("+q"):
                if "q" in bot.server["ISUPPORT"]["PREFIX"]:
                    nick = mode.split()[1]
                    if nick not in bot.channels[channel]["ops"]:
                        bot.channels[channel]["ops"].append(nick)
                elif "q" in bot.server["ISUPPORT"]["CHANMODES"][0]:
                    mask = mode.split()[1]
                    if mask not in bot.channels[channel]["quiets"]:
                        bot.channels[channel]["quiets"].append(mask)
            elif mode.startswith("-q"):
                if "q" in bot.server["ISUPPORT"]["PREFIX"]:
                    nick = mode.split()[1]
                    if nick in bot.channels[channel]["ops"]:
                        bot.channels[channel]["ops"].remove(nick)
                elif "q" in bot.server["ISUPPORT"]["CHANMODES"][0]:
                    mask = mode.split()[1]
                    if mask in bot.channels[channel]["quiets"]:
                        bot.channels[channel]["quiets"].remove(mask)
            elif mode.startswith("+e"):
                mask = mode.split()[1]
                if mask not in bot.channels[channel]["excepts"]:
                    bot.channels[channel]["excepts"].append(mask)
            elif mode.startswith("-e"):
                mask = mode.split()[1]
                if mask in bot.channels[channel]["excepts"]:
                    bot.channels[channel]["excepts"].remove(mask)
            elif mode.startswith("+I"):
                mask = mode.split()[1]
                if mask not in bot.channels[channel]["invites"]:
                    bot.channels[channel]["invites"].append(mask)
            elif mode.startswith("-I"):
                mask = mode.split()[1]
                if mask in bot.channels[channel]["invites"]:
                    bot.channels[channel]["invites"].remove(mask)
            elif (mode.startswith("+o") or
                  mode.startswith("+a") or
                  mode.startswith("+Y")):
                nick = mode.split()[1]
                if nick not in bot.channels[channel]["ops"]:
                    bot.channels[channel]["ops"].append(nick)
                if nick == bot.nick:
                    bot.log.debug("Syncing excepts and invites for %s", channel)
                    bot.mode(channel, "eI")
                    if channel in bot.opqueue:
                        bot.opqueue[channel].put(True)
            elif (mode.startswith("-o") or
                  mode.startswith("-a") or
                  mode.startswith("-Y")):
                nick = mode.split()[1]
                if nick in bot.channels[channel]["ops"]:
                    bot.channels[channel]["ops"].remove(nick)
                if nick == bot.nick:
                    bot.channels[channel]["excepts"] = None
                    bot.channels[channel]["invites"] = None
            elif mode.startswith("+h"):
                nick = mode.split()[1]
                if nick not in bot.channels[channel]["halfops"]:
                    bot.channels[channel]["halfops"].append(nick)
            elif mode.startswith("-h"):
                nick = mode.split()[1]
                if nick in bot.channels[channel]["halfops"]:
                    bot.channels[channel]["halfops"].remove(nick)
            elif mode.startswith("+v"):
                nick = mode.split()[1]
                if nick not in bot.channels[channel]["voices"]:
                    bot.channels[channel]["voices"].append(nick)
            elif mode.startswith("-v"):
                nick = mode.split()[1]
                if nick in bot.channels[channel]["voices"]:
                    bot.channels[channel]["voices"].remove(nick)
            elif mode.startswith("+k"):
                key = mode.split()[1]
                if channel in bot.config["channels"]:
                    bot.config["channels"][channel]["key"] = key
            elif mode.startswith("-k"):
                if channel in bot.config["channels"]:
                    if "key" in bot.config["channels"][channel]:
                        del(bot.config["channels"][channel]["key"])
            else:
                splitmode = mode.split(" ", 1)
                for m in copy.deepcopy(bot.channels[channel]["modes"]):
                    sm = m.split(" ", 1)
                    if splitmode[0].lstrip("+-") == sm[0].lstrip("+"):
                        if splitmode[0].startswith("-"):
                            bot.channels[channel]["modes"].remove(m)
                        elif splitmode[0].startswith("+"):
                            misc.listreplace(bot.channels[channel]["modes"], m, mode)
                        break
                else:
                    bot.channels[channel]["modes"].append(mode)

def on_324(bot, event):
    channel = event.arguments[0]
    modes = bot.split_modes(event.arguments[1:])
    if channel in bot.channels:
        bot.channels[channel]["modes"] = List(modes)
