import collections
import time

import utils.hook as hook

class Network(object):

    def __init__(self):
        self.queue = collections.deque()

    @hook.command
    def latency(self, bot, event, args):
        now = time.time()
        bot.send("PING :{0}".format(now))
        while True:
            try:
                pingts = float(self.queue.pop())
            except IndexError:
                continue
            if pingts != now:
                continue
            diff = time.time() - pingts
            bot.reply(event, "{0:.2f} seconds.".format(diff))
            break

    @hook.event(type="PONG")
    def pong(self, bot, event):
        self.queue.append(event.arguments[0])

Class = Network
