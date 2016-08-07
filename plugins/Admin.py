import utils.hook as hook

class Admin(object):

    @hook.command(command="reload", flags="a")
    def reloadcmd(self, bot, event, args):
        bot.reply(event, "Reloading handlers")
        bot.manager.reloadhandlers()
        bot.reply(event, "Reloading plugins")
        bot.manager.reloadplugins()

    @hook.command(flags="a")
    def rehash(self, bot, event, args):
        bot.reply(event, "Rehashing config")
        bot.manager.reloadconfig()

Class = Admin
