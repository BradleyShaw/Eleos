import queue
import time

import utils.plugins as plugins
import utils.hook as hook

class Network(plugins.Plugin):

    def __init__(self, *args, **kwargs):
        super(Network, self).__init__(*args, **kwargs)
        self.queue = queue.Queue()

    @hook.command
    def latency(self, bot, event, args):
        """takes no arguments

        Measures approximate latency to the IRC server.
        """
        now = time.time()
        bot.send("PING :{0}".format(now))
        self.queue.put((event, now))

    @hook.event(type="PONG")
    def pong(self, bot, event):
        now = time.time()
        if not self.queue.empty():
            replyevn, then = self.queue.get_nowait()
            bot.reply(replyevn, "{0:.2f} seconds.".format(now - then))

Class = Network
