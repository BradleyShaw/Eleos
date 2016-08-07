import subprocess

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

    @hook.command(flags="a")
    def die(self, bot, event, args):
        bot.manager.die("Shutting down ({0} ({1}))".format(event.source.nick,
            args))

    @hook.command(flags="a")
    def restart(self, bot, event, args):
        bot.manager.restart("Restarting ({0} ({1}))".format(event.source.nick,
            args))

    @hook.command(flags="a")
    def update(self, bot, event, args):
        output = subprocess.check_output("git pull -n", stderr=subprocess.STDOUT,
            shell=True)
        if output:
            output = output.decode("UTF-8", "ignore").splitlines()
            for line in output:
                if len(line) > 0:
                    bot.reply(event, line)

    @hook.command(flags="a")
    def flush(self, bot, event, args):
        lines = bot.flushq()
        bot.reply(event, "Flushed {0} lines from send queue".format(lines))

Class = Admin
