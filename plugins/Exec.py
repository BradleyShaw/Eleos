import subprocess

import utils.plugins as plugins
import utils.hook as hook
import utils.repl as repl


class Exec(plugins.Plugin):

    def __init__(self, *args, **kwargs):
        super(Exec, self).__init__(*args, **kwargs)
        self.console = repl.Repl({'self': self})

    @hook.command(command=">>", flags="a")
    def _exec(self, bot, event, args):
        """<code>

        Executes the specified code in a python interpreter and replies
        with the result.
        """
        self.console.locals.update({
            'self': self,
            'bot': bot,
            'event': event,
            'args': args
        })
        output = self.console.run(args).splitlines()
        for line in output:
            if len(line) > 0:
                bot.reply(event, line)

    @hook.command(command=">", flags="a")
    def _shell(self, bot, event, args):
        """<command>

        Runs the specified command in a shell and replies with the result.
        """
        output = subprocess.check_output(args, stderr=subprocess.STDOUT,
                                         shell=True)
        if output:
            output = output.decode('UTF-8', 'ignore').splitlines()
            for line in output:
                if len(line) > 0:
                    bot.reply(event, line)


Class = Exec
