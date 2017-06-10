from time import sleep

import utils.plugins as plugins
import utils.hook as hook


class Channel(plugins.Plugin):

    @hook.command(flags="o")
    def kick(self, bot, event, args):
        """[<channel>] <nick> [<nick>...] [:][<message>]

        Kicks <nick> in <channel>. <channel> is only necessary if the
        command isn't sent in the channel itself. It is recommended to
        use ':' as a seperator between the nicks and kick message to
        avoid unintentionally kicking someone.
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
                if (nick in bot.channels[channel]["names"] and
                        nick not in kicknicks and not nick.startswith(":")):
                    kicknicks.append(nick)
                elif (nick not in bot.channels[channel]["names"] or
                        nick.startswith(":")):
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

        Bans <nick> in <channel>. <channel> is only necessary if the
        command isn't sent in the channel itself.
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
                for prefix in bot.channels[channel]["prefixes"].items():
                    if nick in prefix[1]:
                        prefixmode = bot.server["prefixes"][prefix[0]]["mode"]
                        setmodes.append("-{0} {1}".format(prefixmode, nick))
            if len(setmodes) == 0:
                return
            already_op = bot.is_op(channel, bot.nick)
            if bot.request_op(channel):
                while bot.channels[channel]["invites"] is None:
                    sleep(0.01)
                for exceptmask in bot.channels[channel]["excepts"]:
                    for nick in bot.ban_affects(channel, exceptmask):
                        if nick in affected:
                            setmodes.append("-e {0}".format(exceptmask))
                for invite in bot.channels[channel]["invites"]:
                    for nick in bot.ban_affects(channel, invite):
                        if nick in affected:
                            setmodes.append("-I {0}".format(invite))
                if not already_op:
                    setmodes.append("-o {0}".format(bot.nick))
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def unban(self, bot, event, args):
        """[<channel>] [<nick|hostmask>...]

        Unbans <nick> (or yourself if no nick is specified) in
        <channel>. <channel> is only necessary if the command isn't sent
        in the channel itself.
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

        Bans <nick> in <channel> and kicks anyone affected (using
        <message> if specified). <channel> is only necessary if the
        command isn't sent in the channel itself. It is recommended to
        use ':' as a seperator between the nicks and kick message to
        avoid unintentionally kicking someone.
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
                if ((nick in bot.channels[channel]["names"] or
                        bot.is_banmask(nick)) and nick not in bannicks and
                        not nick.startswith(":")):
                    bannicks.append(nick)
                elif (nick not in bot.channels[channel]["names"] or
                        nick.startswith(":")):
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
                        chanprefixes = bot.channels[channel]["prefixes"]
                        for prefix in chanprefixes.items():
                            if affect in prefix[1]:
                                prefixdata = bot.server['prefixes'][prefix[0]]
                                prefixmode = prefixdata["mode"]
                                setmodes.append("-{0} {1}".format(prefixmode,
                                                affect))
                        affected.append(affect)
            if len(setmodes) == 0:
                return
            already_op = bot.is_op(channel, bot.nick)
            if bot.request_op(channel):
                while bot.channels[channel]["invites"] is None:
                    sleep(0.01)
                for exceptmask in bot.channels[channel]["excepts"]:
                    for nick in bot.ban_affects(channel, exceptmask):
                        if nick in affected:
                            setmodes.append("-e {0}".format(exceptmask))
                for invite in bot.channels[channel]["invites"]:
                    for nick in bot.ban_affects(channel, invite):
                        if nick in affected:
                            setmodes.append("-I {0}".format(invite))
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)
                for nick in affected:
                    bot.kick(channel, nick, kickmsg)
                if not already_op:
                    bot.mode(channel, "-o {0}".format(bot.nick))

    @hook.command(flags="o")
    def quiet(self, bot, event, args):
        """[<channel>] <nick|hostmask> [<nick|hostmask>...]

        Quiets <nick> in <channel>. <channel> is only necessary if the
        command isn't sent in the channel itself.
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
                for prefix in bot.channels[channel]["prefixes"].items():
                    if nick in prefix[1]:
                        prefixmode = bot.server["prefixes"][prefix[0]]["mode"]
                        setmodes.append("-{0} {1}".format(prefixmode, nick))
            if len(setmodes) == 0:
                return
            already_op = bot.is_op(channel, bot.nick)
            if bot.request_op(channel):
                while bot.channels[channel]["invites"] is None:
                    sleep(0.01)
                for exceptmask in bot.channels[channel]["excepts"]:
                    for nick in bot.ban_affects(channel, exceptmask):
                        if nick in affected:
                            setmodes.append("-e {0}".format(exceptmask))
                if not already_op:
                    setmodes.append("-o {0}".format(bot.nick))
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def unquiet(self, bot, event, args):
        """[<channel>] [<nick|hostmask>...]

        Unquiets <nick> (or yourself if no nick is specified) in
        <channel>. <channel> is only necessary if the command isn't sent
        in the channel itself.
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
    def exempt(self, bot, event, args):
        """[<channel>] <nick|hostmask> [<nick|hostmask>...]

        Exempts <nick> in <channel>. <channel> is only necessary if the
        command isn't sent in the channel itself.
        """
        setmodes = []
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
            bot.reply(event, self.get_help("exempt"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            for nick in nicks:
                if bot.is_banmask(nick):
                    banmask = nick
                else:
                    banmask = bot.banmask(nick)
                setmodes.append("+e {0}".format(banmask))
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def unexempt(self, bot, event, args):
        """[<channel>] [<nick|hostmask>...]

        Unexempts <nick> (or yourself if no nick is specified) in
        <channel>. <channel> is only necessary if the command isn't sent
        in the channel itself.
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
            bot.reply(event, self.get_help("unexempt"))
        else:
            if channel not in bot.channels:
                bot.reply("Error: I'm not in {0}.".format(channel))
                return
            already_op = bot.is_op(channel, bot.nick)
            if bot.request_op(channel):
                while bot.channels[channel]["excepts"] is None:
                    sleep(0.01)
                for nick in nicks:
                    for bmask in bot.channels[channel]["excepts"]:
                        if bot.is_affected(nick, bmask):
                            setmodes.append("-e {0}".format(bmask))
                if not already_op:
                    setmodes.append("-o {0}".format(bot.nick))
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def invex(self, bot, event, args):
        """[<channel>] <nick|hostmask> [<nick|hostmask>...]

        Invexes <nick> in <channel>. <channel> is only necessary if the
        command isn't sent in the channel itself.
        """
        setmodes = []
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
            bot.reply(event, self.get_help("invex"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            for nick in nicks:
                if bot.is_banmask(nick):
                    banmask = nick
                else:
                    banmask = bot.banmask(nick)
                setmodes.append("+I {0}".format(banmask))
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def uninvex(self, bot, event, args):
        """[<channel>] [<nick|hostmask>...]

        Uninvexes <nick> (or yourself if no nick is specified) in
        <channel>. <channel> is only necessary if the command isn't sent
        in the channel itself.
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
            bot.reply(event, self.get_help("uninvex"))
        else:
            if channel not in bot.channels:
                bot.reply("Error: I'm not in {0}.".format(channel))
                return
            already_op = bot.is_op(channel, bot.nick)
            if bot.request_op(channel):
                while bot.channels[channel]["invites"] is None:
                    sleep(0.01)
                for nick in nicks:
                    for bmask in bot.channels[channel]["invites"]:
                        if bot.is_affected(nick, bmask):
                            setmodes.append("-I {0}".format(bmask))
                if not already_op:
                    setmodes.append("-o {0}".format(bot.nick))
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def mode(self, bot, event, args):
        """[<channel>] <modes>

        Sets <modes> in <channel>. <channel> is only necessary if the
        command isn't sent in the channel itself.
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
                return
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def op(self, bot, event, args):
        """[<channel>] [<nick>...]

        Ops <nick> (or yourself if no nick is specified) in <channel>.
        <channel> is only necessary if the command isn't sent in the
        channel itself.
        """
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                if len(args) > 1:
                    nicks = args[1:]
                else:
                    nicks = [event.source.nick]
            elif len(args) > 0:
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
            bot.reply(event, self.get_help("op"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            setmodes = ["+o {0}".format(nick) for nick in nicks]
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def deop(self, bot, event, args):
        """[<channel>] [<nick>...]

        Deops <nick> (or yourself if no nick is specified) in <channel>.
        <channel> is only necessary if the command isn't sent in the
        channel itself.
        """
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                if len(args) > 1:
                    nicks = args[1:]
                else:
                    nicks = [event.source.nick]
            elif len(args) > 0:
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
            bot.reply(event, self.get_help("deop"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            setmodes = ["-o {0}".format(nick) for nick in nicks]
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def voice(self, bot, event, args):
        """[<channel>] [<nick>...]

        Voices <nick> (or yourself if no nick is specified) in
        <channel>. <channel> is only necessary if the command isn't sent
        in the channel itself.
        """
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                if len(args) > 1:
                    nicks = args[1:]
                else:
                    nicks = [event.source.nick]
            elif len(args) > 0:
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
            bot.reply(event, self.get_help("voice"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            setmodes = ["+v {0}".format(nick) for nick in nicks]
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)

    @hook.command(flags="o")
    def devoice(self, bot, event, args):
        """[<channel>] [<nick>...]

        Devoices <nick> (or yourself if no nick is specified) in
        <channel>. <channel> is only necessary if the command isn't sent
        in the channel itself.
        """
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                if len(args) > 1:
                    nicks = args[1:]
                else:
                    nicks = [event.source.nick]
            elif len(args) > 0:
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
            bot.reply(event, self.get_help("devoice"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            setmodes = ["-v {0}".format(nick) for nick in nicks]
            if len(setmodes) == 0:
                return
            if not bot.is_op(channel, bot.nick):
                setmodes.append("-o {0}".format(bot.nick))
            if bot.request_op(channel):
                for mode in bot.unsplit_modes(setmodes):
                    bot.mode(channel, mode)


Class = Channel
