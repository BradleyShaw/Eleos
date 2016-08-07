import utils.hook as hook

class User(object):

    @hook.command
    def whoami(self, bot, event, args):
        user = bot.get_user_by_hostmask(event.source)
        if user:
            bot.reply(event, user)
        else:
            bot.reply(event, "I don't recognise you.")

Class = User
