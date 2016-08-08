import queue
import time

import utils.hook as hook

class Network(object):

    def __init__(self):
        self.queue = queue.Queue()

    @hook.command
    def latency(self, bot, event, args):
        now = time.time()
        bot.send("PING :{0}".format(now))
        while True:
            pingts = float(self.queue.get())
            if pingts != now:
                continue
            diff = time.time() - pingts
            bot.reply(event, "{0:.2f} seconds.".format(diff))
            break

    @hook.event(type="PONG")
    def pong(self, bot, event):
        self.queue.put(event.arguments[0])

Class = Network
