#!/usr/bin/env python3
from fnmatch import fnmatch
import importlib
import ipaddress
import threading
import socket
import queue
import copy
import glob
import json
import time
import ssl
import sys
import os
import re

import requests

import utils.collections as collections
import utils.exceptions as exceptions
import utils.threads as threads
import utils.events as events
import utils.hook as hook
import utils.misc as misc
import utils.task as task
import utils.irc as irc
import utils.log as log
import utils.web as web


class BotManager(object):

    def __init__(self, config_file):
        self._stop = threading.Event()
        self.running = False
        self.connections = irc.Dict()
        self.handlers = irc.Dict()
        self.mtimes = {}
        self.config = {}
        self.threads = []
        self.started = time.time()
        self.log = log.getLogger('Manager')
        self.config_path = os.path.join(os.getcwd(), config_file)
        self.datadir = os.path.join(os.getcwd(), 'data')
        self.plugins = collections.Dict()
        if not os.path.exists(self.datadir):
            self.log.info('Couldn\'t find data dir, creating it...')
            os.mkdir(self.datadir)
        self.reloadconfig()
        self.reloadhandlers()
        self.reloadplugins()
        self.addall()
        self.runall()
        self.running = True
        self.configtask = task.run_every(300, self.saveconfig)
        try:
            self._stop.wait()
        except KeyboardInterrupt:
            self.die('Ctrl-C at console.')

    def importhandler(self, handler_name, reload=False):
        try:
            handler = importlib.import_module('handlers.{0}'.format(
                                              handler_name))
            if reload:
                handler = importlib.reload(handler)
            self.handlers[handler_name] = handler
        except Exception:
            self.log.error('Unable to (re)load %s:', handler_name,
                           exc_info=sys.exc_info())

    def importplugin(self, plugin_name, reload=False):
        try:
            hook.events = []
            plugin = importlib.import_module('plugins.{0}'.format(plugin_name))
            if reload:
                plugin = importlib.reload(plugin)
            if not hasattr(plugin, 'Class'):
                self.log.debug('Ignoring plugin %r; no \'Class\' attribute',
                               plugin_name)
                return
            self.plugins[plugin_name] = {}
            self.plugins[plugin_name]['class'] = plugin.Class(self)
            self.plugins[plugin_name]['commands'] = collections.Dict()
            self.plugins[plugin_name]['events'] = collections.Dict()
            self.plugins[plugin_name]['regexes'] = {}
            for evn in hook.events:
                if evn['event'] == 'command':
                    self.log.debug('Found command %r in plugin %r',
                                   evn['command'], plugin_name)
                    self.plugins[plugin_name]['commands'][evn['command']] = {
                        'func': getattr(self.plugins[plugin_name]['class'],
                                        evn['func']),
                        'perms': evn['perms'],
                        'help': evn['help']
                    }
                elif evn['event'] == 'event':
                    self.log.debug('Found event %r in plugin %r',
                                   evn['type'], plugin_name)
                    self.plugins[plugin_name]['events'][evn['type']] = {
                        'func': getattr(self.plugins[plugin_name]['class'],
                                        evn['func'])
                    }
                elif evn['event'] == 'regex':
                    self.log.debug('Found regex %r in plugin %r',
                                   evn['regex'], plugin_name)
                    self.plugins[plugin_name]['regexes'][evn['regex']] = {
                        'func': getattr(self.plugins[plugin_name]['class'],
                                        evn['func'])
                    }
        except Exception:
            self.log.error('Unable to (re)load %s:', plugin_name,
                           exc_info=sys.exc_info())

    def reloadhandlers(self):
        for handler in glob.glob(os.path.join(os.getcwd(), 'handlers',
                                 '*.py')):
            handler_name = handler.split(os.path.sep)[-1][:-3]
            if handler in self.mtimes.keys():
                if os.path.getmtime(handler) != self.mtimes[handler]:
                    self.importhandler(handler_name, True)
                    self.log.debug('Reloaded handler: %s', handler_name)
            else:
                self.importhandler(handler_name)
                self.log.debug('New handler: %s', handler_name)
            self.mtimes[handler] = os.path.getmtime(handler)

    def reloadplugins(self):
        for plugin in glob.glob(os.path.join(os.getcwd(), 'plugins', '*.py')):
            plugin_name = plugin.split(os.path.sep)[-1][:-3]
            if plugin in self.mtimes.keys():
                if os.path.getmtime(plugin) != self.mtimes[plugin]:
                    self.importplugin(plugin_name, True)
                    self.log.debug('Reloaded plugin: %s', plugin_name)
            else:
                self.importplugin(plugin_name)
                self.log.debug('New plugin: %s', plugin_name)
            self.mtimes[plugin] = os.path.getmtime(plugin)

    def reloadconfig(self):
        try:
            with open(self.config_path) as configfile:
                self.config = json.load(configfile,
                                        object_pairs_hook=irc.OrderedDict)
            for name in self.config:
                if name in self.connections:
                    self.connections[name].reloadconfig()
            if self.running:
                self.cleanup()
                self.addall()
                self.runall()
            self.log.debug('(Re)Loaded config.')
        except Exception:
            self.log.error('Unable to (re)load config:',
                           exc_info=sys.exc_info())
            if len(self.threads) == 0:
                sys.exit(1)

    def saveconfig(self):
        try:
            tmpconfig = '{0}.tmp'.format(self.config_path)
            with open(tmpconfig, 'w') as configfile:
                json.dump(self.config, configfile, indent=2)
                configfile.write('\n')
            os.replace(tmpconfig, self.config_path)
            self.log.debug('Config saved to file')
        except Exception:
            self.log.error('Unable to save config:', exc_info=sys.exc_info())

    def addbot(self, name):
        if name not in self.connections:
            self.connections[name] = Bot(name, self.config[name])

    def addall(self):
        for name in self.config:
            self.addbot(name)

    def runbot(self, name):
        bot = self.connections[name]
        if not bot.running:
            t = threading.Thread(target=bot.run, args=(self,))
            t.daemon = True
            t.start()
            self.threads.append(t)

    def runall(self):
        for name in self.connections:
            self.runbot(name)

    def cleanup(self):
        for name in copy.deepcopy(list(self.connections.keys())):
            if name not in self.config:
                self.connections[name].quit('Network removed from config',
                                            True)
                del(self.connections[name])

    def die(self, msg=None):
        self.configtask.stop()
        self.saveconfig()
        for bot in self.connections.values():
            bot.quit(msg, True)
        try:
            self.wait_on_threads(5)
        except KeyboardInterrupt:
            pass
        self._stop.set()

    def restart(self, msg=None):
        self.configtask.stop()
        self.saveconfig()
        for bot in self.connections.values():
            bot.quit(msg, True)
        try:
            self.wait_on_threads(5)
        except KeyboardInterrupt:
            self._stop.set()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def wait_on_threads(self, timeout=None):
        for thread in self.threads:
            thread.join(timeout)


class Bot(object):

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.nick = irc.String(self.config['nick'])
        self.regain = False
        self.connected = False
        self.dying = False
        self.pingtask = None
        self.stickytask = None
        self.identified = False
        self.running = False
        self.log = log.getLogger(self.name)
        t = threading.Thread(target=self.sendqueue)
        t.daemon = True
        t.start()

    def get_account(self, hostmask):
        hmask = events.NickMask(str(hostmask))
        if hmask.nick in self.nicks:
            return self.nicks[hmask.nick]['account']

    def get_flags(self, username, global_only=False, channel=None):
        flags = self.config['flags'].get(username, '')
        if channel and not global_only:
            flags += self.get_channel_config(channel, 'flags', {}).get(
                                             username, '')
        return flags

    def has_flag(self, hmask, flag, global_only=False, channel=None):
        global_only = True
        user = self.get_account(hmask)
        if not user:
            return False
        return flag in self.get_flags(user, global_only, channel)

    def get_channel_config(self, channel, key=None, default=None):
        config = copy.deepcopy(self.config['channels'].get('default', {}))
        config.update(self.config['channels'].get(channel, {}))
        if key:
            return config.get(key, default)
        else:
            return config

    def get_channel_factoids(self, channel, factoid=None):
        factoids = copy.deepcopy(self.config['channels'].get('default',
                                 {}).get('factoids', {}))
        factoids.update(self.config['channels'].get(channel,
                        {}).get('factoids', {}))
        if factoid:
            return factoids.get(factoid)
        else:
            return factoids

    def get_channel_aliases(self, channel, alias=None):
        aliases = copy.deepcopy(self.config['channels'].get('default',
                                {}).get('aliases', {}))
        aliases.update(self.config['channels'].get(channel, {}).get('aliases',
                       {}))
        if alias:
            return aliases.get(alias)
        else:
            return aliases

    def get_channel_ignores(self, channel):
        ignores = copy.deepcopy(self.config['channels'].get('default',
                                {}).get('ignores', []))
        ignores += self.config['channels'].get(channel, {}).get('ignores', [])
        ignores = irc.List(ignores)
        return ignores

    def recv(self):
        if self.sock:
            part = ''
            data = ''
            while not part.endswith('\r\n'):
                part = self.sock.recv(2048)
                self.rx += len(part)
                part = part.decode('UTF-8', 'ignore')
                data += part
            data = data.split('\r\n')
            self.rxmsgs += len(data)
            return data

    def send_raw(self, data):
        try:
            self.log.debug('<-- %s', data)
            data = '{0}\r\n'.format(data).encode('UTF-8', 'ignore')
            self.sock.send(data)
            self.tx += len(data)
            self.txmsgs += 1
        except (AttributeError, BrokenPipeError, OSError):
            self.log.debug('Dropping message %r; not connected', data)

    def run(self, manager):
        self.running = True
        self.manager = manager
        self.rx = 0
        self.tx = 0
        self.rxmsgs = 0
        self.txmsgs = 0
        self.channels = irc.Dict()
        self.nicks = irc.Dict()
        self.server = collections.Dict()
        self.started = time.time()
        self.lastline = time.time()
        self.datadir = os.path.join(self.manager.datadir, self.name)
        self.identified = (
            not self.config.get('nickserv') and
            not self.config.get('sasl') and
            not self.config.get('ssl', {}).get('cert')
        )
        self.sasl = {
            'mechanisms': copy.deepcopy(self.config.get('sasl')) or [],
            'current': None
        }
        self.nick = irc.String(self.config['nick'])
        self.opqueue = irc.Dict()
        if self.config.get('ipv6'):
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.config.get('bindaddr'):
            self.sock.bind((self.config['bindaddr'], 0))
        if isinstance(self.config.get('ssl'), dict):
            sslcfg = self.config['ssl']
            if sslcfg.get('verify', True):
                cert_reqs = ssl.CERT_REQUIRED
            else:
                cert_reqs = ssl.CERT_NONE
            certfile = sslcfg.get('cert')
            keyfile = sslcfg.get('key')
            ca_certs = sslcfg.get('ca_certs', requests.certs.where())
            self.sock = ssl.wrap_socket(self.sock, keyfile=keyfile,
                                        certfile=certfile, cert_reqs=cert_reqs,
                                        ca_certs=ca_certs)
        try:
            self.log.info('Connecting to %s:%d as %s', self.config['host'],
                          self.config['port'], self.config['nick'])
            self.sock.connect((self.config['host'], self.config['port']))
            self.send('CAP LS')
            self.send('NICK {0}'.format(self.config['nick']))
            self.send('USER {0} * * :{1}'.format(
                self.config['ident'], self.config['realname']))
        except Exception:
            self.log.error('Failed to connect to %s:%d', self.config['host'],
                           self.config['port'], exc_info=sys.exc_info())
            self.reconnect()
        else:
            try:
                self.loop()
            except exceptions.CleanExit:
                sys.exit(0)

    def reconnect(self, msg='Reconnecting'):
        try:
            if self.sock:
                self.quit(msg)
                self.log.info('Reconnecting in 10 seconds')
                time.sleep(10)
                self.run(self.manager)
        except Exception:
            pass

    def quit(self, msg=None, die=False):
        if self.connected:
            self.flushq()
            if msg:
                self.send_raw('QUIT :{0}'.format(msg))
            else:
                self.send_raw('QUIT')
            if self.pingtask:
                self.pingtask.stop()
                self.pingtask = None
            if self.stickytask:
                self.stickytask.stop()
                self.stickytask = None
            self.connected = False
            self.sock.close()
        self.sock = None
        if die:
            self.dying = True

    def msg(self, target, msg, notice=False, echo=True):
        if self.noflood(target):
            sendfunc = self.send_raw
        else:
            sendfunc = self.send
        if notice:
            cmd = 'NOTICE'
        else:
            cmd = 'PRIVMSG'
        msg = str(msg).encode('UTF-8', 'ignore')
        maxlen = 400 - len('{0} {1} :\r\n'.format(cmd, target).encode('UTF-8',
                           'ignore'))
        msgs = [msg[i:i+maxlen].decode('UTF-8', 'ignore')
                for i in range(0, len(msg), maxlen)]
        if len(msgs) > 3:
            paste = web.paste(msg.decode('UTF-8', 'ignore'))
            sendfunc('{0} {1} :{2}'.format(cmd, target, paste))
            if echo:
                event = events.Event(':{0}!{1}@{2} {3} {4} :{5}'.format(
                                     self.nick,
                                     self.nicks[self.nick]['user'],
                                     self.nicks[self.nick]['host'],
                                     cmd, target, paste))
                self.handle_event(event)
        else:
            for line in msgs:
                sendfunc('{0} {1} :{2}'.format(cmd, target, line))
                if echo:
                    event = events.Event(':{0}!{1}@{2} {3} {4} :{5}'.format(
                                         self.nick,
                                         self.nicks[self.nick]['user'],
                                         self.nicks[self.nick]['host'],
                                         cmd, target, line))
                    self.handle_event(event)

    def reply(self, event, msg):
        if event.target == self.nick:
            self.msg(event.source.nick, msg, True)
        else:
            self.msg(event.target, msg)

    def ctcp(self, target, ctcptype, msg=None):
        if msg:
            self.msg(target, '\x01{0} {1}\x01'.format(ctcptype, msg))
        else:
            self.msg(target, '\x01{0}\x01'.format(ctcptype))

    def ctcpreply(self, event, ctcptype, msg):
        reply = '\x01{0} {1}\x01'.format(ctcptype, msg)
        self.msg(event.source.nick, reply, True)

    def join(self, channel, key=None):
        if key:
            self.send('JOIN {0} {1}'.format(channel, key))
        else:
            self.send('JOIN {0}'.format(channel))

    def multijoin(self, channels, keys=[]):
        self.send('JOIN {0} {1}'.format(','.join(channels), ','.join(keys)))

    def part(self, channel, msg=None):
        if self.get_channel_config(channel, 'sticky'):
            return
        if msg:
            self.send('PART {0} :{1}'.format(channel, msg))
        else:
            self.send('PART {0}'.format(channel, msg))

    def who(self, target):
        if 'WHOX' in self.server.get('ISUPPORT', {}):
            self.send('WHO {0} %tcnuhiraf,158'.format(target))
        else:
            self.send('WHO {0}'.format(target))

    def whois(self, nick):
        self.send('WHOIS {0}'.format(nick))

    def mode(self, target, modes=None):
        if modes:
            self.send('MODE {0} {1}'.format(target, modes))
        else:
            self.send('MODE {0}'.format(target))

    def kick(self, channel, target, message=None):
        if self.get_channel_config(channel, 'remove'):
            kickcmd = 'REMOVE'
        else:
            kickcmd = 'KICK'
        if not message:
            message = self.get_channel_config(channel, 'kickmsg', 'Goodbye.')
        self.send('{0} {1} {2} :{3}'.format(kickcmd, channel, target, message))

    def flushq(self):
        lines = len(self.sendq)
        self.sendq = []
        return lines

    def sendqueue(self):
        self.sendq = []
        burstdone = False
        while True:
            if len(self.sendq) > 0:
                if not burstdone:
                    for line in self.sendq[:9]:
                        self.send_raw(line)
                        self.sendq.remove(line)
                    burstdone = True
                if len(self.sendq) == 0:
                    burstdone = False
                else:
                    line = self.sendq.pop(0)
                    self.send_raw(line)
                    time.sleep(2)
            else:
                burstdone = False
            time.sleep(0.2)

    def ping(self):
        now = time.time()
        if not self.connected:
            self.lastline = now
            return
        diff = now - self.lastline
        if diff >= 240:
            self.reconnect('Lag timeout: {0} seconds.'.format(int(diff)))
            return
        elif diff >= 120:
            self.send('PING :{0}'.format(now))
        else:
            return

    def sticky(self):
        stickychans = [c for c in self.config['channels'] if
                       self.get_channel_config(c, 'sticky')]
        for channel in stickychans:
            if channel not in self.channels:
                self.join(channel, self.get_channel_config(channel, 'key'))

    def reloadconfig(self):
        self.config = self.manager.config[self.name]
        self.cleanup()
        self.autojoin()

    def cleanup(self):
        for channel in copy.deepcopy(list(self.channels.keys())):
            if channel == 'default':
                continue
            elif channel not in self.config['channels']:
                self.part(channel, 'Channel removed from config')

    def autojoin(self):
        autojoins = []
        keys = []
        for channel in self.config['channels']:
            if channel in self.channels or channel == 'default':
                continue
            elif self.get_channel_config(channel, 'autojoin'):
                autojoins.append(channel)
                key = self.get_channel_config(channel, 'key')
                if key:
                    keys.append(key)
        if len(autojoins) > 0:
            self.multijoin(autojoins, keys)

    def send(self, data):
        self.sendq.append(data)

    def noflood(self, channel):
        moderated = '+m' in self.channels.get(channel, {}).get('modes', '')
        return self.is_op(channel, self.nick) or (self.is_voice(channel,
                                                  self.nick) and not moderated)

    def is_voice(self, channel, nick):
        prefixes = [p[0] for p in self.server['prefixes'].items() if
                    p[1]['level'] == 'voice']
        if channel in self.channels:
            for prefix in prefixes:
                if nick in self.channels[channel]['prefixes'][prefix]:
                    return True
        return False

    def is_op(self, channel, nick):
        prefixes = [p[0] for p in self.server['prefixes'].items() if
                    p[1]['level'] == 'op']
        if channel in self.channels:
            for prefix in prefixes:
                if nick in self.channels[channel]['prefixes'][prefix]:
                    return True
        return False

    def is_halfop(self, channel, nick):
        prefixes = [p[0] for p in self.server['prefixes'].items() if
                    p[1]['level'] == 'halfop']
        if channel in self.channels:
            for prefix in prefixes:
                if nick in self.channels[channel]['prefixes'][prefix]:
                    return True
        return False

    def is_channel(self, string):
        return string[0] in self.server['ISUPPORT']['CHANTYPES']

    def is_ignored(self, channel, mask):
        ignores = self.get_channel_ignores(channel)
        for ignore in ignores:
            if self.is_affected(mask, ignore):
                return True
        return False

    def is_affected(self, nickmask, banmask):
        extban = None
        nickmask = str(nickmask)
        if '!' not in nickmask:
            if nickmask in self.nicks:
                nickmask = '{0}!{1}@{2}'.format(nickmask,
                                                self.nicks[nickmask]['user'],
                                                self.nicks[nickmask]['host'])
            else:
                nickmask = '{0}!*@*'.format(nickmask)
        nickmask = events.NickMask(nickmask)
        nick = nickmask.nick
        if self.server['ISUPPORT'].get('EXTBAN'):
            extban = self.parse_extban(banmask)
        if extban:
            letter = extban['letter']
            banmask = extban.get('arg')
            if banmask:
                banmask = banmask.lower()
            negate = extban.get('negate', False)
            if letter == '&':
                ebprefix = self.server['ISUPPORT']['EXTBAN'][0]
                extbans = banmask.split(',')
                for eb in extbans:
                    eb = '{0}{1}'.format(ebprefix, eb)
                    if not self.is_affected(nickmask, eb):
                        break
                else:
                    if not negate:
                        return True
                if negate:
                    return True
                return False
            elif letter == '|':
                ebprefix = self.server['ISUPPORT']['EXTBAN'][0]
                extbans = banmask.split(',')
                for eb in extbans:
                    eb = '{0}{1}'.format(ebprefix, eb)
                    if self.is_affected(nickmask, eb) and not negate:
                        return True
                if negate:
                    return True
                return False
            elif letter == 'a':
                account = self.get_account(nickmask)
                if account:
                    account = irc.String(account).lower()
                if negate and not account:
                    return True
                elif account and banmask:
                    if fnmatch(account, banmask):
                        if not negate:
                            return True
                    elif negate:
                        return True
                elif account and not negate:
                    return True
            elif not banmask:
                return False
            elif letter == 'c':
                if banmask not in self.channels:
                    return False
                if nickmask.nick in self.channels[banmask]['names']:
                    if not negate:
                        return True
                elif negate:
                    return True
            elif letter == 'j':
                if banmask not in self.channels:
                    return False
                for ban in self.channels[banmask]['bans']:
                    if self.is_affected(nickmask, ban):
                        if not negate:
                            return True
                if negate:
                    return True
            elif letter == 'm':
                if self.is_affected(nickmask, banmask) and not negate:
                    return True
                if negate:
                    return True
                return False
            elif letter == 'r':
                if nick not in self.nicks:
                    return False
                realname = irc.String(self.nicks[nick]['realname']).lower()
                if fnmatch(realname, banmask):
                    if not negate:
                        return True
                elif negate:
                    return True
            elif letter == 'x':
                if nick not in self.nicks:
                    return False
                realname = self.nicks[nick]['realname']
                cmpmask = '{0}#{1}'.format(irc.String(str(nickmask)).lower(),
                                           irc.String(realname).lower())
                if fnmatch(cmpmask, banmask):
                    if not negate:
                        return True
                elif negate:
                    return True
        else:
            nickmask = irc.String(str(nickmask)).lower()
            banmask = irc.String(str(banmask)).lower()
            if fnmatch(nickmask, banmask):
                return True
            try:
                nickmask = events.NickMask(str(nickmask))
                banmask = events.NickMask(str(banmask))
                ipaddr = nickmask.host
                ipaddr = ipaddress.ip_address(ipaddr)
                banip = banmask.host
                banip = ipaddress.ip_network(banip)
                nickmask1 = '{0}!{1}'.format(nickmask.nick, nickmask.user)
                banmask1 = '{0}!{1}'.format(banmask.nick, banmask.user)
                if ipaddr in banip and fnmatch(nickmask1, banmask1):
                    return True
            except ValueError:
                pass
        nickmask = events.NickMask(str(nickmask))
        if nickmask.nick in self.nicks:
            ipaddr = self.nicks[nickmask.nick].get('ip')
            if ipaddr and ipaddr != nickmask.host:
                nickmask.host = ipaddr
                return self.is_affected(nickmask, banmask)
        if (nickmask.host.startswith('gateway/web/freenode')):
            try:
                nickmask.host = misc.hex2ip(nickmask.user)
                return self.is_affected(nickmask, banmask)
            except Exception:
                pass
        return False

    def is_banmask(self, mask):
        if re.match('^\S+!\S+@\S+$', mask):
            return True
        elif self.server['ISUPPORT'].get('EXTBAN'):
            return bool(self.parse_extban(mask))
        return False

    def parse_extban(self, eb):
        try:
            eb = str(eb)
        except Exception:
            return
        ebprefix = self.server['ISUPPORT']['EXTBAN'][0]
        if ebprefix in '.^$*+?{}[]()\\|':
            ebprefix = '\\{0}'.format(ebprefix)
        for ebletter in self.server['ISUPPORT']['EXTBAN'][1]:
            if ebletter in '.^$*+?{}[]()\\|':
                ebletter = '\\{0}'.format(ebletter)
            if re.match('^{0}~?{1}(:(.+)?)?$'.format(ebprefix, ebletter), eb):
                extban = {}
                extban['letter'] = ebletter
                if ':' in eb:
                    extban['arg'] = irc.String(eb.split(':', 1)[1])
                if re.match('^{0}~{1}'.format(ebprefix, ebletter), eb):
                    extban['negate'] = True
                return extban

    def ban_affects(self, channel, banmask):
        if channel not in self.channels:
            return []
        matches = irc.List()
        for nick in self.channels[channel]['names']:
            if self.is_affected(nick, banmask):
                matches.append(nick)
        return matches

    def banmask(self, nickmask):
        nickmask = str(nickmask)
        if '!' not in nickmask:
            if nickmask in self.nicks:
                nickmask = '{0}!{1}@{2}'.format(nickmask,
                                                self.nicks[nickmask]['user'],
                                                self.nicks[nickmask]['host'])
            else:
                return '{0}!*@*'.format(nickmask)
        nickmask = events.NickMask(nickmask)
        nick = nickmask.nick
        user = nickmask.user
        host = nickmask.host
        if host.startswith('gateway/'):
            if '/irccloud.com/' in host:
                uid = user[1:]
                host = '/'.join(host.split('/')[:-1])
                return '*!*{0}@{1}'.format(uid, host)
            elif '/ip.' in host:
                host = host.split('/ip.')[1]
                return '*!*@*{0}'.format(host)
            else:
                host = '/'.join(host.split('/')[:-1])
                return '*!{0}@{1}'.format(user, host)
        elif host.startswith('nat/'):
            host = '/'.join(host.split('/')[:-1])
            return '*!{0}@{1}'.format(user, host)
        elif '/' in host:
            return '*!*@{0}'.format(host)
        else:
            ipaddr = None
            if nick in self.nicks:
                ipaddr = self.nicks[nick].get('ip')
            if ipaddr:
                try:
                    ipaddr = ipaddress.IPv6Network(ipaddr)
                    ipaddr = ipaddr.supernet(new_prefix=64)
                    host = str(ipaddr).replace(':/64', '*', 1)
                except ValueError:
                    host = ipaddr
            else:
                try:
                    ipaddr = ipaddress.IPv6Network(host)
                    ipaddr = ipaddr.supernet(new_prefix=64)
                    host = str(ipaddr).replace(':/64', '*', 1)
                except ValueError:
                    pass
            if user.startswith('~'):
                return '*!*@{0}'.format(host)
            else:
                return '*!{0}@{1}'.format(user, host)

    def getargmodes(self):
        chanmodes = self.server['ISUPPORT']['CHANMODES']
        prefix = list(self.server['ISUPPORT']['PREFIX'].keys())
        return {
            'set': ''.join(chanmodes[0:3] + prefix),
            'unset': ''.join(chanmodes[0:2] + prefix)
        }

    def split_modes(self, modes):
        argmodes = self.getargmodes()
        splitmodes = []
        argscount = 1
        setmode = True
        for mode in modes[0]:
            if mode == '+':
                setmode = True
                continue
            elif mode == '-':
                setmode = False
                continue
            if setmode:
                if mode in argmodes['set']:
                    modearg = modes[argscount]
                    argscount += 1
                    splitmodes.append('+{0} {1}'.format(mode, modearg))
                else:
                    splitmodes.append('+{0}'.format(mode))
            else:
                if mode in argmodes['unset']:
                    modearg = modes[argscount]
                    argscount += 1
                    splitmodes.append('-{0} {1}'.format(mode, modearg))
                else:
                    splitmodes.append('-{0}'.format(mode))
        return splitmodes

    def unsplit_modes(self, modes):
        unsplitmodes = ['']
        finalmodes = []
        argscount = 0
        setmode = True
        for mode in modes:
            if mode.startswith('+'):
                if len(unsplitmodes[0]) == 0:
                    unsplitmodes[0] = '+'
                elif not setmode:
                    unsplitmodes[0] += '+'
                setmode = True
            elif mode.startswith('-'):
                if len(unsplitmodes[0]) == 0:
                    unsplitmodes[0] = '-'
                elif setmode:
                    unsplitmodes[0] += '-'
                setmode = False
            mode = mode.lstrip('+-')
            mode = mode.split()
            unsplitmodes[0] += mode[0]
            if len(mode) > 1:
                unsplitmodes.append(mode[1])
                argscount += 1
                if argscount == int(self.server['ISUPPORT']['MODES']):
                    finalmodes.append(' '.join(unsplitmodes))
                    unsplitmodes = ['']
                    argscount = 0
        if unsplitmodes != ['']:
            finalmodes.append(' '.join(unsplitmodes))
        return finalmodes

    def request_op(self, channel):
        if channel not in self.channels:
            return False
        elif self.is_op(channel, self.nick):
            return True
        self.opqueue[channel] = queue.Queue()
        self.msg('ChanServ', 'OP {0}'.format(channel))
        try:
            gotop = self.opqueue[channel].get(timeout=30)
            del(self.opqueue[channel])
            return gotop
        except queue.Empty:
            del(self.opqueue[channel])
            return False

    def hunt_command(self, command, plugin=None):
        if not plugin:
            plugins = []
            for name, data in self.manager.plugins.items():
                if command in data['commands']:
                    plugins.append(name)
            if len(plugins) != 1:
                return plugins if plugins else None
            plugin = plugins[0]
        if plugin not in self.manager.plugins:
            return
        data = self.manager.plugins[plugin]
        if command not in data['commands']:
            return
        return data['commands'][command]

    def check_perms(self, hmask, perms, channel=None):
        global_only = perms['global']
        flags = perms['flags']
        for flag in flags:
            if self.has_flag(hmask, flag, global_only, channel) or flag == 'A':
                return True
        return False

    def get_factoid(self, channel, factoid, args):
        factoids = self.get_channel_factoids(channel)
        if factoid not in factoids:
            return
        factoid = factoids[factoid]
        args = args.strip(' ').split(' ')
        if len(args) > 0:
            if args[0] in self.nicks:
                factoid = '{0}: {1}'.format(args[0], factoid)
        return factoid

    def get_alias(self, channel, alias, args):
        aliases = self.get_channel_aliases(channel)
        if alias not in aliases:
            return
        alias = aliases[alias]
        if len(args) > 0:
            alias = '{0} {1}'.format(alias, args)
        return self.parse_command(alias)

    def parse_command(self, cmd):
        cmd = cmd.split(' ', 1)
        plugin = None
        command = cmd[0]
        if len(cmd) > 1:
            args = cmd[1]
            cmd = ' '.join(cmd).split(' ', 2)
            if self.hunt_command(cmd[1], cmd[0]):
                plugin = cmd[0]
                command = cmd[1]
                if len(cmd) > 2:
                    args = cmd[2]
                else:
                    args = ''
        else:
            args = ''
        return (plugin, command, args)

    def handle_event(self, event):
        for handler in self.manager.handlers.values():
            if hasattr(handler, 'on_{0}'.format(event.type)):
                func = getattr(handler, 'on_{0}'.format(event.type))
                func(self, event)
        for plugin in self.manager.plugins.values():
            if 'ALL' in plugin['events']:
                threads.run(plugin['events']['ALL']['func'], self, event)
            if event.type in plugin['events']:
                threads.run(plugin['events'][event.type]['func'], self, event)

    def loop(self):
        try:
            while True:
                data = self.recv()
                if data is None:
                    break
                for line in data:
                    self.manager.reloadhandlers()
                    if len(line) == 0:
                        continue
                    self.log.debug('--> %s', line)
                    self.lastline = time.time()
                    event = events.Event(line)
                    self.handle_event(event)
        except socket.error:
            self.connected = False
            self.reconnect()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please specify a config file.')
        sys.exit(1)
    BotManager(sys.argv[1])
