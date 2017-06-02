import re

import utils.plugins as plugins
import utils.hook as hook

class User(plugins.Plugin):

    @hook.command(flags="a", global_only=True)
    def setflags(self, bot, event, args):
        """<username> <channel>|--global <flags>

        Sets <flags> on <username> in <channel> or globally.
        """
        try:
            args = self.space_split(args)
            username = args[0]
            channel = args[1]
            flags = args[2]
        except IndexError:
            bot.reply(event, self.get_help("setflags"))
        else:
            if not re.fullmatch("[A-Za-z+-]+", flags):
                bot.reply(event, "Error: Invalid flags specified.")
                return
            add = True
            flagchg = {"add": "", "del": ""}
            if channel == "--global":
                if username not in bot.config["flags"]:
                    bot.config["flags"][username] = ""
                userflags = bot.config["flags"][username]
                channel = None
            else:
                if channel not in bot.config["channels"]:
                    bot.reply(event, "Error: There is no such channel.")
                    return
                if "flags" not in bot.config["channels"][channel]:
                    bot.config["channels"][channel]["flags"] = {}
                if username not in bot.config["channels"][channel]["flags"]:
                    bot.config["channels"][channel]["flags"][username] = ""
                userflags = bot.config["channels"][channel]["flags"][username]
            for flag in flags:
                if flag == "+":
                    add = True
                elif flag == "-":
                    add = False
                elif add and not bot.has_flag(username, flag, channel=channel):
                    userflags += flag
                    flagchg["add"] += flag
                elif flag in userflags and not add:
                    userflags = userflags.replace(flag, "")
                    flagchg["del"] += flag
            if channel:
                bot.config["channels"][channel]["flags"][username] = userflags
            else:
                bot.config["flags"][username] = userflags
            flagstr = ""
            if flagchg["add"]:
                flagstr += "+{0}".format(flagchg["add"])
            if flagchg["del"]:
                flagstr += "-{0}".format(flagchg["del"])
            reply = []
            if flagstr:
                reply.append("Flags {0} were set on".format(flagstr))
            else:
                reply.append("Flags unchanged for")
            reply.append(username)
            if channel:
                reply.append("in {0}".format(channel))
            bot.reply(event, "{0}.".format(" ".join(reply)))

    @hook.command
    def whoami(self, bot, event, args):
        """takes no arguments

        Returns your current username in the bot config
        """
        user = bot.get_account(event.source)
        if user:
            bot.reply(event, user)
        else:
            bot.reply(event, "Error: You don't appear to be identified to NickServ. "
                "If you are, use the 'auth' command and try again.")

    @hook.command
    def auth(self, bot, event, args):
        """takes no arguments

        Attempts to identify the user.
        """
        if bot.get_account(event.source):
            bot.reply(event, "Error: You are already identified.")
        else:
            bot.who(event.source.nick)

    @hook.command
    def flags(self, bot, event, args):
        """[<username>]

        Returns flags for <username> or yourself if no
        username is specified.
        """
        if args == "":
            user = bot.get_account(event.source)
            if not user:
                bot.reply(event, "Error: You don't appear to be identified to "
                    "NickServ. If you are, use the 'auth' command and try again.")
                return
        else:
            user = self.space_split(args)[0]
        globalflags = bot.config["flags"].get(user, "")
        if bot.is_channel(event.target):
            chanflags = bot.config["channels"].get(event.target, {}).get(
                "flags", {}).get(user, "")
            bot.reply(event, "Flags for {0}: {1}: {2} | Global: {3}".format(
                        user, event.target, chanflags, globalflags))
        else:
            bot.reply(event, "Flags for {0}: {1}".format(user, globalflags))

Class = User
