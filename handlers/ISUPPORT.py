import re

from utils.collections import Dict, List


def on_005(bot, event):
    if 'ISUPPORT' not in bot.server:
        bot.server['ISUPPORT'] = Dict()
    for param in event.arguments[:-1]:
        if '=' in param:
            name, value = param.split('=')
        else:
            name = param
            value = ''
        if value != '':
            if ',' in value:
                for param1 in value.split(','):
                    if ':' in value:
                        if ':' in param1:
                            name1, value1 = param1.split(':')
                        else:
                            name1 = param1
                            value1 = ''
                        if name not in bot.server['ISUPPORT']:
                            bot.server['ISUPPORT'][name] = Dict()
                        bot.server['ISUPPORT'][name][name1] = value1
                    else:
                        if name not in bot.server['ISUPPORT']:
                            bot.server['ISUPPORT'][name] = List()
                        bot.server['ISUPPORT'][name].append(param1)
            else:
                if ':' in value:
                    name1, value1 = value.split(':')
                    bot.server['ISUPPORT'][name] = Dict()
                    bot.server['ISUPPORT'][name][name1] = value1
                elif name == 'PREFIX':
                    count = 0
                    value = value.split(')')
                    value[0] = value[0].lstrip('(')
                    types = re.split(r'^(.*o)(.*h)?(.*)$', value[0])[1:-1]
                    levels = {
                        'op': types[0],
                        'halfop': types[1] or '',
                        'voice': types[2]
                    }
                    bot.server['ISUPPORT'][name] = {}
                    bot.server['prefixes'] = {}
                    for mode in value[0]:
                        name1 = mode
                        value1 = value[1][count]
                        count += 1
                        for level in levels.items():
                            if mode in level[1]:
                                bot.server['prefixes'][value1] = {
                                    'mode': mode,
                                    'level': level[0]
                                }
                                break
                        bot.server['ISUPPORT'][name][name1] = value1
                else:
                    bot.server['ISUPPORT'][name] = value
        else:
            bot.server['ISUPPORT'][name] = value
