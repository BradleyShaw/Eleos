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

Class = Exec
