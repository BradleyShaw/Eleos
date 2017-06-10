import signal
import os

import utils.plugins as plugins
import utils.hook as hook
import utils.task as task


class Test(plugins.Plugin):

    @hook.event(type="JOIN")
    def on_join(self, bot, event):
        # Allow 10 seconds for something to fuck up then exit cleanly
        task.run_in(10, os.kill, (os.getpid(), signal.SIGINT))


Class = Test
