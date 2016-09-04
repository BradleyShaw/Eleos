import utils.hook as hook

class User(object):

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
            user = args
        account = bot.config["users"].get(user)
        if account:
            bot.reply(event, "Flags for {0}: {1}".format(user, account["flags"]))
        else:
            bot.reply(event, "There is no such user.")

Class = User
