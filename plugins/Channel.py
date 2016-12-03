import utils.plugins as plugins
import utils.hook as hook

class Channel(plugins.Plugin):

    @hook.command(flags="o")
    def kick(self, bot, event, args):
        """[<channel>] <nick> [<nick>...] [:][<message>]

        Kicks <nick> in <channel>. <channel> is only necessary if the command
        isn't sent in the channel itself. It is recommended to use ':' as a
        seperator between the nicks and kick message to avoid unintentionally
        kicking someone.
        """
        kicknicks = []
        kickmsg = None
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                nicks = args[1:]
            else:
                if bot.is_channel(args[0]):
                    channel = args[0]
                    nicks = args[1:]
                else:
                    channel = event.target
                    nicks = args
        except IndexError:
            bot.reply(event, self.get_help("kick"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            for nick in nicks:
                if (nick in bot.channels[channel]["names"]
                    and nick not in kicknicks
                    and not nick.startswith(":")):
                    kicknicks.append(nick)
                elif nick not in bot.channels[channel]["names"] or nick.startswith(":"):
                    kickmsg = " ".join(nicks[len(kicknicks):])
                    if kickmsg.startswith(":"):
                        kickmsg = kickmsg.replace(":", "", 1)
                    break
            nicks = kicknicks
            already_op = bot.is_op(channel, bot.nick)
            if bot.request_op(channel):
                for nick in nicks:
                    bot.kick(channel, nick, kickmsg)
                if not already_op:
                    bot.mode(channel, "-o {0}".format(bot.nick))

Class = Channel
