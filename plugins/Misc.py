from hurry.filesize import size, alternative
import subprocess
import psutil
import os

import utils.hook as hook
import utils.misc as misc
import utils.time as time

class Misc(object):

    @hook.command(command="list")
    def listcmd(self, bot, event, args):
        """[<plugin>]

        Lists the commands in the specified plugin. If no plugin is specified,
        lists all loaded plugins.
        """
        if args in bot.manager.plugins:
            bot.reply(event,
                ", ".join(sorted(bot.manager.plugins[args]["commands"].keys())))
        else:
            bot.reply(event,
                ", ".join(sorted(bot.manager.plugins.keys())))

    @hook.command(command="help")
    def helpcmd(self, bot, event, args):
        """[<plugin>] [<command>]

        Gives the help information for the specified command. A plugin doesn't
        need to be specified unless the command is in more than one plugin.
        Use the 'list' command to get a list of plugins and commands.
        """
        if args == "":
            bot.reply(event,
                bot.manager.plugins["Misc"]["commands"]["help"]["help"])
            return
        args = args.split(" ")
        plugin = None
        if len(args) > 1:
            plugin = args[0]
            command = args[1]
        else:
            command = args[0]
        if plugin:
            if plugin in bot.manager.plugins:
                if command in bot.manager.plugins[plugin]["commands"]:
                    bot.reply(event,
                        bot.manager.plugins[plugin]["commands"][command]["help"])
                else:
                    bot.reply(event, "Error: There is no such command.")
            else:
                bot.reply(event, "Error: There is no such plugin.")
        else:
            for plugin in bot.manager.plugins.values():
                if command in plugin["commands"]:
                    bot.reply(event, plugin["commands"][command]["help"])
                    break
            else:
                bot.reply(event, "Error: There is no such command.")

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
        botuptime = time.timesince(bot.manager.started)
        connuptime = time.timesince(bot.started)
        process = psutil.Process(os.getpid())
        ramusage = size(process.memory_info().rss, system=alternative)
        datarecv = size(bot.rx, system=alternative)
        datasent = size(bot.tx, system=alternative)
        cputime = subprocess.getoutput("ps -p $$ h -o time")
        users = misc.count(len(bot.nicks), "user", "users")
        chans = misc.count(len(bot.channels), "channel", "channels")
        txmsgs = misc.count(bot.txmsgs, "message", "messages")
        rxmsgs = misc.count(bot.txmsgs, "message", "messages")
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
        bot.reply(event, "https://github.com/IndigoTiger/Eleos")

Class = Misc
