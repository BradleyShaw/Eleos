from .irc import String

class Event(object):

    def __init__(self, raw):
        self.raw = raw
        self.source = None
        self.type = None
        self.target = None
        self.arguments = []
        args = ""
        args1 = ""
        if " :" in raw:
            raw, args1 = raw.split(" :", 1)
        if raw.startswith(":"):
            raw = raw.replace(":", "", 1)
            raw = raw.split(" ")
            self.source = raw[0]
            self.type = raw[1]
            if len(raw) > 2:
                self.target = raw[2]
            if len(raw) > 3:
                args = " ".join(raw[3:])
            self.source = NickMask(self.source)
        else:
            self.type, args = raw.split(" ", 1)
            self.source = self.target = None
        if self.target:
            self.target = String(self.target)
        if len(args1) > 0:
            if len(args) > 0:
                args = "{0} :{1}".format(args, args1)
            else:
                args = ":{0}".format(args1)
        if args.lstrip(":").startswith("\x01") and args.endswith("\x01"):
            args = args.lstrip(":")
            args = args.strip("\x01")
            if self.type == "PRIVMSG":
                if args.startswith("ACTION"):
                    self.type = "ACTION"
                    args = args.replace("ACTION", "", 1).lstrip(" ")
                else:
                    self.type = "CTCP"
            elif self.type == "NOTICE":
                self.type == "CTCPREPLY"
        if args.startswith(":"):
            args = args.split(":", 1)
        else:
            args = args.split(" :", 1)
        for arg in args[0].split(" "):
            if len(arg) > 0:
                self.arguments.append(arg)
        if len(args) > 1:
            self.arguments.append(args[1])

    def __repr__(self):
        tmpl = (
            "type: {type}, "
            "source: {source}, "
            "target: {target}, "
            "arguments: {arguments}, "
            "raw: {raw}"
        )
        return tmpl.format(**vars(self))

class NickMask(object):

    def __init__(self, hostmask):
        hostmask = String(hostmask)
        if "!" in hostmask:
            self.nick, self.userhost = hostmask.split("!", 1)
            self.user, self.host = self.userhost.split("@", 1)
        else:
            self.nick = hostmask
            self.userhost = self.user = self.host = None

    def __str__(self):
        if self.userhost:
            return "{0}!{1}@{2}".format(self.nick, self.user, self.host)
        else:
            return self.nick
