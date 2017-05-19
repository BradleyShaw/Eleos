import subprocess

import utils.plugins as plugins
import utils.hook as hook

class Admin(plugins.Plugin):

    @hook.command(command="reload", flags="a", global_only=True)
    def reloadcmd(self, bot, event, args):
        """takes no arguments

        Reloads handlers and plugins.
        """
        bot.reply(event, "Reloading handlers")
        self.manager.reloadhandlers()
        bot.reply(event, "Reloading plugins")
        self.manager.reloadplugins()

    @hook.command(flags="a", global_only=True)
    def rehash(self, bot, event, args):
        """takes no arguments

        Rehashes the bot's configuration.
        """
        bot.reply(event, "Rehashing config")
        self.manager.reloadconfig()

    @hook.command(flags="a", global_only=True)
    def die(self, bot, event, args):
        """[<message>]

        Shuts down the bot (with <message> if specified)
        """
        if len(args) > 0:
            self.manager.die("Shutting down ({0} ({1}))".format(event.source.nick,
                args))
        else:
            self.manager.die("Shutting down ({0})".format(event.source.nick))

    @hook.command(flags="a", global_only=True)
    def restart(self, bot, event, args):
        """[<message>]

        Restarts the bot (with <message> if specified)
        """
        if len(args) > 0:
            self.manager.restart("Restarting ({0} ({1}))".format(event.source.nick,
                args))
        else:
            self.manager.restart("Restarting ({0})".format(event.source.nick))

    @hook.command(flags="a", global_only=True)
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

    @hook.command(flags="a", global_only=True)
    def flush(self, bot, event, args):
        """takes no arguments

        Flushes the sendqueue.
        """
        lines = bot.flushq()
        bot.reply(event, "Flushed {0} lines from send queue.".format(lines))

    @hook.command(command="join", flags="a", global_only=True)
    def joincmd(self, bot, event, args):
        """<channel> [<key>]

        Makes the bot attempt to join <channel>
        (using <key> if specified).
        """
        args = args.split(" ", 1)
        if len(args) == 1:
            bot.join(args[0])
        else:
            bot.join(args[0], args[1])

    @hook.command(flags="a", global_only=True)
    def raw(self, bot, event, args):
        """<command>

        Sends <command> to the IRC server.
        """
        if len(self.space_split(args)) == 0:
            bot.reply(event, self.get_help("raw"))
            return
        bot.send(args)

Class = Admin
