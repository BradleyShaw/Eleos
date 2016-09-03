import utils.helpers as helpers

def on_MODE(bot, event):
    if bot.is_channel(event.target):
        channel = event.target
        modes = helpers.split_modes(event.arguments)
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
                mask = mode.split()[1]
                if mask not in bot.channels[channel]["quiets"]:
                    bot.channels[channel]["quiets"].append(mask)
            elif mode.startswith("-q"):
                mask = mode.split()[1]
                if mask in bot.channels[channel]["quiets"]:
                    bot.channels[channel]["quiets"].remove(mask)
            elif mode.startswith("+o"):
                nick = mode.split()[1]
                if nick not in bot.channels[channel]["ops"]:
                    bot.channels[channel]["ops"].append(nick)
            elif mode.startswith("-o"):
                nick = mode.split()[1]
                if nick in bot.channels[channel]["ops"]:
                    bot.channels[channel]["ops"].remove(nick)
            elif mode.startswith("+v"):
                nick = mode.split()[1]
                if nick not in bot.channels[channel]["voices"]:
                    bot.channels[channel]["voices"].append(nick)
            elif mode.startswith("-v"):
                nick = mode.split()[1]
                if nick in bot.channels[channel]["voices"]:
                    bot.channels[channel]["voices"].remove(nick)
