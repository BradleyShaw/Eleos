import json
import time
import os

from utils.time import timesince
import utils.plugins as plugins
import utils.hook as hook
import utils.misc as misc
import utils.irc as irc

class Seen(plugins.Plugin):

    def __init__(self, *args, **kwargs):
        super(Seen, self).__init__(*args, **kwargs)
        self.datapath = os.path.join(self.datadir, "seen.json")
        self.load_data()

    def load_data(self):
        if os.path.exists(self.datapath):
            with open(self.datapath) as seendata:
                self.seen = json.load(seendata, object_pairs_hook=irc.Dict)
        else:
            self.seen = irc.Dict()
            self.save_data()

    def save_data(self):
        tmpdata = "{0}.tmp".format(self.datapath)
        with open(tmpdata, "w") as seendata:
            json.dump(self.seen, seendata)
        os.replace(tmpdata, self.datapath)

    def get_last_activity(self, net, channel, nick, msg=False):
        try:
            if msg:
                lastseen = self.seen[net][channel][nick]["msg"]
            else:
                lastseen = self.seen[net][channel][nick]["any"]
        except KeyError:
            return "I have not seen {0}.".format(nick)
        else:
            msg = "{0} was last seen in {1} {2} ago: ".format(lastseen["nick"],
                lastseen["channel"], timesince(lastseen["time"]))
            if lastseen["type"] == "message":
                msg += "<{0}> {1}".format(lastseen["nick"], lastseen["msg"])
            elif lastseen["type"] == "action":
                msg += "* {0} {1}".format(lastseen["nick"], lastseen["msg"])
            elif lastseen["type"] == "join":
                msg += "--> {0} ({1}@{2}) has joined {3}".format(lastseen["nick"],
                    lastseen["user"], lastseen["host"], lastseen["channel"])
            elif lastseen["type"] == "part":
                msg += "<-- {0} ({1}@{2}) has left {3}".format(lastseen["nick"],
                    lastseen["user"], lastseen["host"], lastseen["channel"])
                if lastseen["msg"]:
                    msg += " ({0})".format(lastseen["msg"])
            elif lastseen["type"] == "quit":
                msg += "<-- {0} ({1}@{2}) has quit".format(lastseen["nick"],
                    lastseen["user"], lastseen["host"])
                if lastseen["msg"]:
                    msg += " ({0})".format(lastseen["msg"])
            return msg

    def add_activity(self, event, network, nick, user, host, msg=None, channel=None):
        data = irc.Dict({
            "time": time.time(),
            "type": event,
            "nick": nick,
            "user": user,
            "host": host,
            "msg": msg
        })
        if network not in self.seen:
            self.seen[network] = irc.Dict()
        if channel:
            if channel not in self.seen[network]:
                self.seen[network][channel] = irc.Dict()
            if nick not in self.seen[network][channel]:
                self.seen[network][channel][nick] = irc.Dict()
            data["channel"] = channel
            self.seen[network][channel][nick]["any"] = data
            if event in ["message", "action"]:
                self.seen[network][channel][nick]["msg"] = data
        else:
            for chan in self.seen[network]:
                if nick in self.seen[network][chan]:
                    if self.seen[network][chan][nick]["any"]["type"] not in ["part", "quit"]:
                        data["channel"] = chan
                        self.seen[network][chan][nick]["any"] = data
        self.save_data()

    @hook.command(command="seen")
    def seenmsg(self, bot, event, args):
        """[<channel>] <nick>

        Returns the last time <nick> was seen on <channel> and what <nick> was
        last seen saying. <channel> is only necessary if the command isn't sent
        in the channel itself.
        """
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                nick = args[1]
            elif bot.is_channel(args[0]):
                channel = args[0]
                nick = args[1]
            else:
                channel = event.target
                nick = args[0]
        except IndexError:
            bot.reply(event, self.get_help("seen"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            if event.source.nick not in bot.channels[channel]["names"]:
                bot.reply(event, "Error: You are not in {0}.".format(channel))
                return
            bot.reply(event, self.get_last_activity(bot.name, channel, nick, msg=True))

    @hook.command(command="any")
    def seenany(self, bot, event, args):
        """[<channel>] <nick>

        Returns the last time <nick> was seen on <channel> and what <nick> was
        doing. This isn't limited to just messages. <channel> is only necessary
        if the command isn't sent in the channel itself.
        """
        try:
            args = self.space_split(args)
            if event.target == bot.nick:
                channel = args[0]
                nick = args[1]
            elif bot.is_channel(args[0]):
                channel = args[0]
                nick = args[1]
            else:
                channel = event.target
                nick = args[0]
        except IndexError:
            bot.reply(event, self.get_help("any"))
        else:
            if channel not in bot.channels:
                bot.reply(event, "Error: I'm not in {0}.".format(channel))
                return
            if event.source.nick not in bot.channels[channel]["names"]:
                bot.reply(event, "Error: You are not in {0}.".format(channel))
                return
            bot.reply(event, self.get_last_activity(bot.name, channel, nick))

    @hook.event(type="PRIVMSG")
    def on_privmsg(self, bot, event):
        if event.target == bot.nick:
            return
        self.add_activity(
            event="message",
            network=bot.name,
            nick=event.source.nick,
            user=event.source.user,
            host=event.source.host,
            msg=event.arguments[0],
            channel=event.target)

    @hook.event(type="ACTION")
    def on_action(self, bot, event):
        if event.target == bot.nick:
            return
        self.add_activity(
            event="action",
            network=bot.name,
            nick=event.source.nick,
            user=event.source.user,
            host=event.source.host,
            msg=event.arguments[0],
            channel=event.target)

    @hook.event(type="JOIN")
    def on_join(self, bot, event):
        self.add_activity(
            event="join",
            network=bot.name,
            nick=event.source.nick,
            user=event.source.user,
            host=event.source.host,
            channel=event.target)

    @hook.event(type="PART")
    def on_part(self, bot, event):
        partmsg = None
        if len(event.arguments) > 0:
            if len(event.arguments[0]) > 0:
                partmsg = event.arguments[0]
        self.add_activity(
            event="part",
            network=bot.name,
            nick=event.source.nick,
            user=event.source.user,
            host=event.source.host,
            msg=partmsg,
            channel=event.target)

    @hook.event(type="QUIT")
    def on_quit(self, bot, event):
        quitmsg = None
        if len(event.arguments) > 0:
            if len(event.arguments[0]) > 0:
                quitmsg = event.arguments[0]
        self.add_activity(
            event="quit",
            network=bot.name,
            nick=event.source.nick,
            user=event.source.user,
            host=event.source.host,
            msg=quitmsg)

Class = Seen
