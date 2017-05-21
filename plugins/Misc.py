from hurry.filesize import size, alternative
import subprocess
import psutil
import os

import utils.plugins as plugins
import utils.hook as hook
import utils.misc as misc
import utils.time as time

class Misc(plugins.Plugin):

    @hook.command(command="list")
    def listcmd(self, bot, event, args):
        """[<plugin>]

        Lists the commands in the specified plugin. If no plugin is specified,
        lists all loaded plugins.
        """
        if args.strip() in self.manager.plugins:
            commands = sorted(self.manager.plugins[args]["commands"].keys())
            if len(commands) > 0:
                bot.reply(event, ", ".join(commands))
            else:
                bot.reply(event, "This plugin has no commands.")
        else:
            bot.reply(event,
                ", ".join(sorted(self.manager.plugins.keys())))

    @hook.command(command="help")
    def helpcmd(self, bot, event, args):
        """[<plugin>] [<command>]

        Gives the help information for the specified command. A plugin doesn't
        need to be specified unless the command is in more than one plugin.
        Use the 'list' command to get a list of plugins and commands.
        """
        if args == "":
            bot.reply(event,
                self.get_help("help"))
            return
        args = args.split(" ")
        plugin = None
        if len(args) > 1:
            plugin = args[0]
            command = args[1]
        else:
            command = args[0]
        cmdhelp = None
        if not plugin:
            plugins = []
            for name, plugin in self.manager.plugins.items():
                if command in plugin["commands"]:
                    plugins.append(name)
            if len(plugins) == 0:
                bot.reply(event, "Error: No such command.")
                return
            elif len(plugins) > 1:
                bot.reply(event, "Error: This command exists in more than one "
                    "plugin.")
                return
            else:
                plugin = plugins[0]
        cmdhelp = self.get_help(command, plugin)
        if cmdhelp:
            bot.reply(event, cmdhelp)
        else:
            bot.reply(event, "Error: No such command.")

    @hook.command
    def ping(self, bot, event, args):
        """takes no arguments

        Check if the bot is alive.
        """
        bot.reply(event, "Pong!")

    @hook.command
    def status(self, bot, event, args):
        """takes no arguments

        Replies with various data about the bot's status.
        """
        botuptime = time.timesince(self.manager.started)
        connuptime = time.timesince(bot.started)
        process = psutil.Process(os.getpid())
        ramusage = size(process.memory_info().rss, system=alternative)
        datarecv = size(bot.rx, system=alternative)
        datasent = size(bot.tx, system=alternative)
        cputime = subprocess.getoutput("ps -p $$ h -o time")
        users = misc.count(len(bot.nicks), "user", "users")
        chans = misc.count(len(bot.channels), "channel", "channels")
        txmsgs = misc.count(bot.txmsgs, "message", "messages")
        rxmsgs = misc.count(bot.rxmsgs, "message", "messages")
        bot.reply(event, "This bot has been running for {0}, has been connected "
            "for {1}, is tracking {2} in {3}, is using {4} of RAM, has used {5} "
            "of CPU time, has sent {6} for {7} of data and received {8} for {9} "
            "of data".format(botuptime, connuptime, users, chans, ramusage,
            cputime, txmsgs, datasent, rxmsgs, datarecv))

    @hook.command
    def version(self, bot, event, args):
        """takes no arguments

        Returns the currently running version of the bot.
        """
        version = subprocess.getoutput("git describe")
        bot.reply(event, "Eleos {0}".format(version))

    @hook.command
    def source(self, bot, event, args):
        """takes not arguments

        Returns a link to the bot's source.
        """
        bot.reply(event, "https://git.intrpt.net/bs/Eleos")

    @hook.command
    def hm(self, bot, event, args):
        """[<nick>]

        Returns the hostmask of <nick> (or yourself if no nick is specified).
        """
        args = self.space_split(args)
        if len(args) > 0:
            nick = args[0]
            if nick not in bot.nicks:
                bot.reply(event, "Error: No such user.")
                return
            for user in bot.nicks:
                if user == nick:
                    nick = user
                    break
            hmask = "{nick}!{user}@{host}".format(nick=nick, **bot.nicks[nick])
            bot.reply(event, hmask)
        else:
            bot.reply(event, event.source)

    @hook.command
    def bm(self, bot, event, args):
        """[<nick|hostmask>]

        Returns a banmask for <nick> (or yourself if no nick is specified).
        """
        args = self.space_split(args)
        if len(args) > 0:
            nick = args[0]
        else:
            nick = event.source
        bot.reply(event, bot.banmask(nick))

    @hook.command
    def ftds(self, bot, event, args):
        """[<channel>|--global]

        Lists factoids for <channel> or globally. <channel> is only required if
        the command isn't sent in the channel itself.
        """
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
            elif len(args) > 0:
                if args[0].lower() == "--global":
                    channel = "default"
                else:
                    channel = args[0]
            else:
                channel = event.target
        except IndexError:
            bot.reply(event, self.get_help("ftds"))
        else:
            factoids = sorted(bot.get_channel_factoids(channel).keys())
            if len(factoids) > 0:
                bot.reply(event, ", ".join(factoids))
            else:
                bot.reply(event, "No factoids found.")

Class = Misc
