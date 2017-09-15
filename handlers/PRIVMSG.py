import re

import utils.threads as threads


def on_PRIVMSG(bot, event):
    if bot.is_ignored(event.target, event.source):
        bot.log.debug('Ignoring message from %s', event.source)
        return
    msg = event.arguments[0]
    for plugin in bot.manager.plugins.values():
        for regex, cfg in plugin['regexes'].items():
            matches = re.findall(regex, msg)
            if matches:
                threads.run(cfg['func'], bot, event, matches)
    prefix = bot.get_channel_config(event.target, 'prefix')
    if ((len(prefix) > 0 and msg.startswith(prefix)) or
            msg.startswith(bot.nick) or event.target == bot.nick):
        bot.log.debug('Possible command: %r', msg)
        msg = msg.split(' ', 1)
        if msg[0].startswith(bot.nick):
            if msg[0].rstrip(':,') == bot.nick:
                if len(msg) > 1:
                    msg = msg[1].split(' ', 1)
                else:
                    return
            else:
                return
        if len(prefix) > 0:
            if msg[0].startswith(prefix):
                msg[0] = msg[0].replace(prefix, '', 1)
        plugin, command, args = bot.parse_command(' '.join(msg))
        data = bot.hunt_command(command, plugin)
        if type(data) is list:
            plugins = '{0} and {1}'.format(', '.join(data[:-1]), data[-1])
            bot.reply(event, 'Error: The command \'{0}\' is available in the '
                      '{1} plugins. Please use \'<plugin> {0}\' to call the '
                      'command you would like to use.'.format(command,
                                                              plugins))
            return
        if not data:
            possible = []
            if plugin:
                if len(args) > 0:
                    possible.append((plugin, '{0} {1}'.format(command, args)))
                else:
                    possible.append((plugin, command))
            possible.append((command, args))
            for alias in possible:
                aliasdata = bot.get_alias(event.target, *alias)
                if not aliasdata:
                    continue
                data = bot.hunt_command(aliasdata[1], aliasdata[0])
                if data:
                    args = aliasdata[2]
                    break
        if data:
            channel = (event.target if bot.is_channel(event.target)
                       else None)
            target = (event.target if event.target != bot.nick else
                      'private')
            if bot.check_perms(event.source, data['perms'], channel):
                bot.log.info('%s called %r in %s', event.source, command,
                             target)
                threads.run(data['func'], bot, event, args)
                return
            else:
                bot.log.debug('%s tried to use command %r but does not have '
                              'required flag(s) (%s)', event.source, command,
                              data['perms']['flags'])
                bot.reply(event, 'Error: You are not authorized to perform '
                          'this command.')
            return
        factoid = bot.get_factoid(event.target, command, args)
        if factoid:
            target = (event.target if event.target != bot.nick else
                      'private')
            bot.log.info('%s called %r in %s', event.source, command, target)
            bot.reply(event, factoid)
            return
        bot.log.debug('%s tried to use invalid command %r', event.source,
                      command)
