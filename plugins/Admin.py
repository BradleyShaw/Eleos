import subprocess

import utils.hook as hook

class Admin(object):

    @hook.command(command="reload", flags="a")
    def reloadcmd(self, bot, event, args):
        """takes no arguments

        Reloads handlers and plugins.
        """
        bot.reply(event, "Reloading handlers")
        bot.manager.reloadhandlers()
        bot.reply(event, "Reloading plugins")
        bot.manager.reloadplugins()

    @hook.command(flags="a")
    def rehash(self, bot, event, args):
        """takes no arguments

        Rehashes the bot's configuration.
        """
        bot.reply(event, "Rehashing config")
        bot.manager.reloadconfig()

    @hook.command(flags="a")
    def die(self, bot, event, args):
        """[<message>]

        Shuts down the bot (with <message> if specified)
        """
        if len(args) > 0:
            bot.manager.die("Shutting down ({0} ({1}))".format(event.source.nick,
                args))
        else:
            bot.manager.die("Shutting down ({0})".format(event.source.nick))

    @hook.command(flags="a")
    def restart(self, bot, event, args):
        """[<message>]

        Restarts the bot (with <message> if specified)
        """
        if len(args) > 0:
            bot.manager.restart("Restarting ({0} ({1}))".format(event.source.nick,
                args))
        else:
            bot.manager.restart("Restarting ({0})".format(event.source.nick))

    @hook.command(flags="a")
    def update(self, bot, event, args):
        """takes no arguments

        Attempts a `git pull` to update the bot.
        """
        output = subprocess.check_output("git pull -n", stderr=subprocess.STDOUT,
            shell=True)
        if output:
            output = output.decode("UTF-8", "ignore").splitlines()
            for line in output:
                if len(line) > 0:
                    bot.reply(event, line)

    @hook.command(flags="a")
    def flush(self, bot, event, args):
        """takes no arguments

        Flushes the sendqueue.
        """
        lines = bot.flushq()
        bot.reply(event, "Flushed {0} lines from send queue.".format(lines))

    @hook.command(command="join", flags="a")
    def joincmd(self, bot, event, args):
        """<channel> [<key>]

        Makes the bot attempt to join <channel>
        (using <key> if specified).
        """
        args = args.split(" ", 1)
        if len(args) == 1:
            bot.join(args[0])
        else:
            bot.join(agrs[0], args[1])

Class = Admin
