#!/usr/bin/python3
import importlib
import threading
import traceback
import socket
import glob
import json
import time
import ssl
import sys
import os

import utils.events
import utils.log
import utils.irc
import utils.hook
import utils.collections
import utils.exceptions

class BotManager(object):

    def __init__(self, config_file):
        self.connections = {}
        self.plugins = {}
        self.handlers = {}
        self.mtimes = {}
        self.config = {}
        self.threads = []
        self.events = []
        self.started = time.time()
        self.log = utils.log.getLogger("Manager")
        self.config_path = os.path.join(os.getcwd(), config_file)
        self.datadir = os.path.join(os.getcwd(), "data")
        if not os.path.exists(self.datadir):
            self.log.info("Couldn't find data dir, creating it...")
            os.mkdir(self.datadir)
        self.reloadconfig()
        self.reloadhandlers()
        self.reloadplugins()
        for name, server in self.config.items():
            self.connections[name] = Bot(name, server)
        self.runall()

    def importplugin(self, plugin_name, path, reload=False):
        try:
            self.plugins[plugin_name] = importlib.import_module(plugin_name)
            if reload:
                utils.hook.events = []
                self.plugins[plugin_name] = importlib.reload(self.plugins[plugin_name])
        except:
            self.log.error("Unable to (re)load %s:", plugin_name)
            traceback.print_exc()
        self.mtimes[plugin_name] = os.path.getmtime(path)

    def importhandler(self, handler_name, path, reload=False):
        try:
            self.handlers[handler_name] = importlib.import_module(handler_name)
            if reload:
                self.handlers[handler_name] = importlib.reload(self.handlers[handler_name])
        except:
            self.log.error("Unable to (re)load %s:", handler_name)
            traceback.print_exc()
        self.mtimes[handler_name] = os.path.getmtime(path)

    def reloadplugins(self):
        for plugin in glob.glob(os.path.join(os.getcwd(), "plugins", "*.py")):
            import_name = "plugins.{0}".format(plugin.split(os.path.sep)[-1][:-3])
            if import_name in self.mtimes.keys():
                if os.path.getmtime(plugin) != self.mtimes[import_name]:
                    utils.hook.events = []
                    self.importplugin(import_name, plugin, True)
                    for event in utils.hook.events:
                        self.log.debug("New %s found: %s", event._event, event.__name__)
                        utils.hook.events[utils.hook.events.index(event)].__module__ = import_name
                        for evn in [e for e in self.events if e.__module__ == import_name]:
                            if ((utils.hook.events[utils.hook.events.index(event)].__name__ == evn.__name__) or
                            (evn.__module__ == import_name and evn.__name__ not in [e.__name__ for e in
                            utils.hook.events])):
                                self.log.debug("Deleting an old %s: %s", evn._event, evn.__name__)
                                del(self.events[self.events.index(cmd)])
                    self.log.debug("Reloaded plugin: %s", str(plugin))
                    self.events = utils.hook.events + self.events
            else:
                utils.hook.events = []
                self.importplugin(import_name, plugin)
                for event in utils.hook.events:
                    self.log.debug("New %s found: %s", event._event, event.__name__)
                    utils.hook.events[utils.hook.events.index(event)].__module__ = import_name
                self.log.debug("New plugin: %s", str(plugin))
                self.events = utils.hook.events + self.events

    def reloadhandlers(self):
        for handler in glob.glob(os.path.join(os.getcwd(), "handlers", "*.py")):
            import_name = "handlers.{0}".format(handler.split(os.path.sep)[-1][:-3])
            if import_name in self.mtimes.keys():
                if os.path.getmtime(handler) != self.mtimes[import_name]:
                    self.importhandler(import_name, handler, True)
                    self.log.debug("Reloaded handler: %s", str(handler))
            else:
                self.importhandler(import_name, handler)
                self.log.debug("New handler: %s", str(handler))

    def reloadconfig(self):
        try:
            with open(self.config_path) as configfile:
                self.config = json.load(configfile)
            for name, server in self.config.items():
                if name in self.connections:
                    self.connections[name].config = server
            self.log.debug("(Re)Loaded config.")
        except:
            self.log.error("Unable to (re)load config:")
            traceback.print_exc()
            if len(self.threads) == 0:
                sys.exit(1)

    def runall(self):
        for bot in self.connections.values():
            t = threading.Thread(target=bot.run, args=(self,))
            t.daemon = True
            t.start()
            self.threads.append(t)
        try:
            self.wait_on_threads()
        except KeyboardInterrupt:
            self.die("Ctrl-C at console.")

    def die(self, msg=None):
        for bot in self.connections.values():
            bot.quit(msg, True)
        self.wait_on_threads()
        sys.exit(0)

    def wait_on_threads(self):
        for thread in self.threads:
            thread.join()

class Bot(object):

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.nick = utils.irc.String(self.config["nick"])
        self.regain = False
        self.connected = False
        self.dying = False
        self.identified = not self.config.get("nickserv") and not self.config.get("sasl")
        self.log = utils.log.getLogger(self.name)
        t = threading.Thread(target=self.sendqueue)
        t.daemon = True
        t.start()

    def recv(self):
        part = ""
        data = ""
        while not part.endswith("\r\n"):
            part = self.sock.recv(2048)
            self.rx += len(part)
            part = part.decode("UTF-8", "ignore")
            data += part
        data = data.split("\r\n")
        self.rxmsgs += len(data)
        return data

    def send_raw(self, data):
        try:
            self.log.debug("<-- %s", data)
            data = "{0}\r\n".format(data).encode("UTF-8", "ignore")
            self.sock.send(data)
            self.tx += len(data)
            self.txmsgs += 1
        except AttributeError:
            self.log.debug("Dropping message %r; not connected", data)

    def run(self, manager):
        self.manager = manager
        self.rx = 0
        self.tx = 0
        self.rxmsgs = 0
        self.txmsgs = 0
        self.caps = []
        self.channels = utils.irc.Dict()
        self.nicks = utils.irc.Dict()
        self.started = time.time()
        self.datadir = os.path.join(self.manager.datadir, self.name)
        if self.config.get("ipv6"):
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.config.get("ssl"):
            self.sock = ssl.wrap_socket(self.sock)
        try:
            self.log.info("Connecting to %s:%d as %s", self.config["host"],
                self.config["port"], self.config["nick"])
            self.sock.connect((self.config["host"], self.config["port"]))
            self.send("CAP LS")
            self.send("NICK {0}".format(self.config["nick"]))
            self.send("USER {0} * * :{1}".format(
                self.config["ident"], self.config["realname"]))
        except:
            self.log.error("Failed to connect to %s:%d", self.config["host"],
                self.config["port"])
            traceback.print_exc()
            self.reconnect()
        else:
            try:
                self.loop()
            except utils.exceptions.CleanExit:
                sys.exit(0)

    def reconnect(self):
        try:
            self.quit("Reconnecting")
            self.log.info("Reconnecting in 10 seconds")
            time.sleep(10)
            self.run(self.manager)
        except:
            pass

    def quit(self, msg=None, die=False):
        self.flushq()
        if msg:
            self.send("QUIT :{0}".format(msg))
        else:
            self.send("QUIT")
        self.connected = False
        if die:
            self.dying = True

    def msg(self, target, msg):
        if self.noflood(target):
            sendfunc = self.send_raw
        else:
            sendfunc = self.send
        sendfunc("PRIVMSG {0} :{1}".format(target, msg))

    def join(self, channel, key=None):
        if key:
            self.send("JOIN {0} {1}".format(channel, key))
        else:
            self.send("JOIN {0}".format(channel))

    def multijoin(self, channels):
        self.send("JOIN {0}".format(",".join(channels)))

    def flushq(self):
        lines = len(self.sendq)
        self.sendq = []
        return lines

    def sendqueue(self):
        self.sendq = []
        burstdone = False
        while True:
            if not burstdone:
                for line in self.sendq[:5]:
                    self.send_raw(line)
                    self.sendq.remove(line)
            if len(self.sendq) == 0:
                burstdone = False
                continue
            else:
                line = self.sendq.pop(0)
                self.send_raw(line)
                time.sleep(1)
            time.sleep(0.2)

    def send(self, data):
        self.sendq.append(data)

    def noflood(self, channel):
        return self.is_voiced(channel, self.nick) or self.is_opped(channel, self.nick)

    def is_voiced(self, channel, nick):
        if channel in self.channels:
            return nick in self.channels[channel]["voices"]
        else:
            return False

    def is_opped(self, channel, nick):
        if channel in self.channels:
            return nick in self.channels[channel]["ops"]

    def loop(self):
        try:
            while True:
                data = self.recv()
                for line in data:
                    if len(line) == 0:
                        continue
                    self.log.debug("--> %s", line)
                    event = utils.events.Event(line)
                    for handler in self.manager.handlers.values():
                        if hasattr(handler, "on_{0}".format(event.type)):
                            func = getattr(handler, "on_{0}".format(event.type))
                            func(self, event)
                    for func in [e for e in self.manager.events if e._event == "event"]:
                        if func._type == "ALL" or func._type == event.type:
                            t = threading.Thread(target=func, args=(self, event))
                            t.daemon = True
                            t.start()
        except socket.error:
            self.connected = False
            self.reconnect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please specify a config file.")
        sys.exit(1)
    BotManager(sys.argv[1])
