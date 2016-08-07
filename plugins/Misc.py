from hurry.filesize import size, alternative
import subprocess
import psutil
import os

import utils.hook as hook
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
        botuptime = time.timesince(bot.manager.started)
        connuptime = time.timesince(bot.started)
        process = psutil.Process(os.getpid())
        ramusage = size(process.memory_info().rss, system=alternative)
        datarecv = size(bot.rx, system=alternative)
        datasent = size(bot.tx, system=alternative)
        cputime = subprocess.getoutput("ps -p $$ h -o time")
        bot.reply(event, "This bot has been running for {0}, has been connected "
            "for {1}, is using {2} of RAM, has used {3} of CPU time, has sent "
            "{4} messages for {5} of data and received {5} messages for {6} of "
            "data".format(botuptime, connuptime, ramusage, cputime, bot.txmsgs,
            datasent, bot.rxmsgs, datarecv))

Class = Misc
