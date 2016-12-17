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

    @hook.command(flags="o")
    def ban(self, bot, event, args):
        """[<channel>] <nick|hostmask> [<nick|hostmask>...]

        Bans <nick> in <channel>. <channel> is only necessary if the command
        isn't sent in the channel itself.
        """
        setmodes = []
        affected = []
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
            bot.reply(event, self.get_help("ban"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            for nick in nicks:
                if bot.is_banmask(nick):
                    banmask = nick
                else:
                    banmask = bot.banmask(nick)
                setmodes.append("+b {0}".format(banmask))
                for affect in bot.ban_affects(channel, banmask):
                    if affect not in affected and affect != bot.nick:
                        affected.append(affect)
            for nick in affected:
                if bot.is_op(channel, nick):
                    setmodes.append("-o {0}".format(nick))
                if bot.is_halfop(channel, nick):
                    setmodes.append("-h {0}".format(nick))
                if bot.is_voice(channel, nick):
                    setmodes.append("-v {0}".format(nick))
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def unban(self, bot, event, args):
        """[<channel>] [<nick|hostmask>...]

        Unbans <nick> (or yourself if no nick is specified) in <channel>.
        <channel> is only necessary if the command isn't sent in the channel
        itself.
        """
        setmodes = []
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                if len(args) > 1:
                    nicks = args[1:]
                else:
                    nicks = [event.source.nick]
            else:
                if len(args) > 0:
                    if bot.is_channel(args[0]):
                        channel = args[0]
                        if len(args) > 1:
                            nicks = args[1:]
                        else:
                            nicks = [event.source.nick]
                    else:
                        channel = event.target
                        nicks = args
                else:
                    channel = event.target
                    nicks = [event.source.nick]
        except IndexError:
            bot.reply(event, self.get_help("unban"))
        else:
            if channel not in bot.channels:
                bot.reply("Error: I'm not in {0}.".format(channel))
                return
            for nick in nicks:
                for bmask in bot.channels[channel]["bans"]:
                    if bot.is_affected(nick, bmask):
                        setmodes.append("-b {0}".format(bmask))
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def kban(self, bot, event, args):
        """[<channel>] <nick|hostmask> [<nick|hostmask>...] [:][<message>]

        Bans <nick> in <channel> and kicks anyone affected (using <message>
        if specified). <channel> is only necessary if the command isn't sent
        in the channel itself. It is recommended to use ':' as a seperator
        between the nicks and kick message to avoid unintentionally kicking
        someone.
        """
        bannicks = []
        setmodes = []
        affected = []
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
            bot.reply(event, self.get_help("kban"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            for nick in nicks:
                if ((nick in bot.channels[channel]["names"]
                    or bot.is_banmask(nick))
                    and nick not in bannicks
                    and not nick.startswith(":")):
                    bannicks.append(nick)
                elif nick not in bot.channels[channel]["names"] or nick.startswith(":"):
                    kickmsg = " ".join(nicks[len(bannicks):])
                    if kickmsg.startswith(":"):
                        kickmsg = kickmsg.replace(":", "", 1)
                    break
            nicks = bannicks
            for nick in nicks:
                if bot.is_banmask(nick):
                    banmask = nick
                else:
                    banmask = bot.banmask(nick)
                setmodes.append("+b {0}".format(banmask))
                for affect in bot.ban_affects(channel, banmask):
                    if affect not in affected and affect != bot.nick:
                        if bot.is_op(channel, affect):
                            setmodes.append("-o {0}".format(affect))
                        if bot.is_halfop(channel, affect):
                            setmodes.append("-h {0}".format(affect))
                        if bot.is_voice(channel, affect):
                            setmodes.append("-v {0}".format(affect))
                        affected.append(affect)
            if len(setmodes) == 0:
                return
            already_op = bot.is_op(channel, bot.nick)
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)
                for nick in affected:
                    bot.kick(channel, nick, kickmsg)
                if not already_op:
                    bot.mode(channel, "-o {0}".format(bot.nick))

    @hook.command(flags="o")
    def quiet(self, bot, event, args):
        """[<channel>] <nick|hostmask> [<nick|hostmask>...]

        Quiets <nick> in <channel>. <channel> is only necessary if the command
        isn't sent in the channel itself.
        """
        setmodes = []
        affected = []
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
            bot.reply(event, self.get_help("quiet"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            for nick in nicks:
                if bot.is_banmask(nick):
                    banmask = nick
                else:
                    banmask = bot.banmask(nick)
                setmodes.append("+q {0}".format(banmask))
                for affect in bot.ban_affects(channel, banmask):
                    if affect not in affected and affect != bot.nick:
                        affected.append(affect)
            for nick in affected:
                if bot.is_op(channel, nick):
                    setmodes.append("-o {0}".format(nick))
                if bot.is_halfop(channel, nick):
                    setmodes.append("-h {0}".format(nick))
                if bot.is_voice(channel, nick):
                    setmodes.append("-v {0}".format(nick))
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def unquiet(self, bot, event, args):
        """[<channel>] [<nick|hostmask>...]

        Unquiets <nick> (or yourself if no nick is specified) in <channel>.
        <channel> is only necessary if the command isn't sent in the channel
        itself.
        """
        setmodes = []
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                if len(args) > 1:
                    nicks = args[1:]
                else:
                    nicks = [event.source.nick]
            else:
                if len(args) > 0:
                    if bot.is_channel(args[0]):
                        channel = args[0]
                        if len(args) > 1:
                            nicks = args[1:]
                        else:
                            nicks = [event.source.nick]
                    else:
                        channel = event.target
                        nicks = args
                else:
                    channel = event.target
                    nicks = [event.source.nick]
        except IndexError:
            bot.reply(event, self.get_help("unquiet"))
        else:
            if channel not in bot.channels:
                bot.reply("Error: I'm not in {0}.".format(channel))
                return
            for nick in nicks:
                for bmask in bot.channels[channel]["quiets"]:
                    if bot.is_affected(nick, bmask):
                        setmodes.append("-q {0}".format(bmask))
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def mode(self, bot, event, args):
        """[<channel>] <modes>

        Sets <modes> in <channel>. <channel> is only necessary if the command
        isn't sent in the channel itself.
        """
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                setmodes = bot.split_modes(args[1:])
            elif bot.is_channel(args[0]):
                channel = args[0]
                setmodes = bot.split_modes(args[1:])
            else:
                channel = event.target
                setmodes = bot.split_modes(args)
        except IndexError:
            bot.reply(event, self.get_help("mode"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

Class = Channel
