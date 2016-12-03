import os
import re

import utils.log as log

class Plugin(object):

    def __init__(self, manager):
        self.manager = manager
        self.datadir = os.path.join(self.manager.datadir,
            self.__class__.__name__)
        self.log = log.getLogger(self.__class__.__name__)
        if not os.path.exists(self.datadir):
            self.log.info("Couldn't find datadir; creating it...")
            os.mkdir(self.datadir)

    def get_help(self, cmd, plugin=None):
        try:
            if not plugin:
                plugin = self.__class__.__name__
            return self.manager.plugins[plugin]["commands"][cmd]["help"]
        except:
            return

    def space_split(self, s):
        splitstr = s.split(" ")
        for item in splitstr:
            if len(item) == 0:
                splitstr.remove(item)
        return splitstr

    def strip_colours(self, s):
        ccodes = ["\x0f", "\x16", "\x1d", "\x1f", "\x02",
            "\x03([1-9][0-6]?)?,?([1-9][0-6]?)?"]
        for cc in ccodes:
            s = re.sub(cc, "", s)
        return s
