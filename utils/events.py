from .irc import String

class Event(object):

    def __init__(self, raw):
        self.raw = raw
        if raw.startswith(":"):
            raw = raw.replace(":", "", 1)
            if len(raw.split(" ", 3)) > 3:
                self.source, self.type, self.target, args = raw.split(" ", 3)
            else:
                self.source, self.type, self.target = raw.split(" ", 3)
                args = ""
            self.source = NickMask(self.source)
        else:
            self.type, args = raw.split(" ", 1)
            self.source = self.target = None
        if self.target:
            self.target = String(self.target)
        self.arguments = []
        args = args.split(":", 1)
        for arg in args[0].split(" "):
            if len(arg) > 0:
                self.arguments.append(arg)
        if len(args) > 1:
            self.arguments.append(args[1])

    def __str__(self):
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
