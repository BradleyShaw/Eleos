import subprocess

import utils.hook as hook
import utils.repl as repl

class Exec(object):

    @hook.command(command=">>", flags="a")
    def _exec(self, bot, event, args):
        """<code>

        Executes the specified code in a python interpreter and replies with
        the result.
        """
        console = repl.Repl({
            "self": self,
            "bot": bot,
            "event": event,
            "args": args
        })
        output = console.run(args).splitlines()
        for line in output:
            if len(line) > 0:
                bot.reply(event, line)

    @hook.command(command=">", flags="a")
    def _shell(self, bot, event, args):
        """<command>

        Runs the specified command in a shell and replies with the result.
        """
        output = subprocess.check_output(args, stderr=subprocess.STDOUT, shell=True)
        if output:
            output = output.decode("UTF-8", "ignore").splitlines()
            for line in output:
                if len(line) > 0:
                    bot.reply(event, line)

Class = Exec
