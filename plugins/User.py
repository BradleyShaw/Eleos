import utils.hook as hook

class User(object):

    @hook.command
    def whoami(self, bot, event, args):
        user = bot.get_user_by_hostmask(event.source)
        if user:
            bot.reply(event, user)
        else:
            bot.reply(event, "I don't recognise you.")

    @hook.command
    def flags(self, bot, event, args):
        if args == "":
            user = bot.get_user_by_hostmask(event.source)
            if not user:
                bot.reply(event, "I don't recognise you.")
        else:
            user = bot.config["users"].get(args)
        if user:
            bot.reply(event, user["flags"])
        else:
            bot.reply(event, "There is no such user.")

Class = User
