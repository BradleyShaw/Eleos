import utils.plugins as plugins
import utils.hook as hook

class User(plugins.Plugin):

    @hook.command
    def whoami(self, bot, event, args):
        """takes no arguments

        Returns your current username in the bot config
        """
        user = bot.get_user_by_hostmask(event.source)
        if user:
            bot.reply(event, user)
        else:
            bot.reply(event, "I don't recognise you.")

    @hook.command
    def flags(self, bot, event, args):
        """[<username>]

        Returns flags for <username> or yourself if no
        username is specified.
        """
        if args == "":
            user = bot.get_user_by_hostmask(event.source)
            if not user:
                bot.reply(event, "I don't recognise you.")
        else:
            user = self.space_split(args)[0]
        account = bot.config["users"].get(user)
        if account:
            globalflags =bot.get_user_flags(user)
            if bot.is_channel(event.target):
                chanflags = bot.get_user_flags(user, channel=event.target)
                bot.reply(event, "Flags for {0}: {1}: {2} | Global: {3}".format(
                            user, event.target, chanflags, globalflags))
            else:
                bot.reply(event, "Flags for {0}: {1}".format(user, globalflags))
        else:
            bot.reply(event, "There is no such user.")

Class = User
