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

        Makes the bot attempt to join <channel> (using <key> if specified).
        """
        args = args.split(" ", 1)
        if len(args) == 1:
            bot.join(args[0])
        else:
            bot.join(args[0], args[1])

    @hook.command(flags="a", global_only=True)
    def part(self, bot, event, args):
        """[<channel>] [<message>]

        Makes the bot part <channel> (with <message> is specified). <channel> is
        only required if the command isn't sent in the channel itself.
        """
        try:
            split_args = self.space_split(args)
            if event.target == bot.nick:
                channel = split_args[0]
                if len(split_args) > 1:
                    message = args.lstrip(" ").split(" ", 1)[1]
            elif len(split_args) > 0:
                if bot.is_channel(split_args[0]):
                    channel = split_args[0]
                    if len(split_args) > 1:
                        message = args.lstrip(" ").split(" ", 1)[1]
                else:
                    channel = event.target
                    message = args
            else:
                channel = event.target
                message = None
        except IndexError:
            bot.reply(event, self.get_help("part"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            bot.part(channel, message)

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
