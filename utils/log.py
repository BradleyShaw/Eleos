import logging
import os


def getLogger(name):
    logdir = os.path.join(os.getcwd(), "log")
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    _format = "[%(asctime)s][%(levelname)s] (%(name)s) %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=_format)
    logformat = logging.Formatter(_format)
    logfile = logging.FileHandler(os.path.join(logdir, "{0}.log".format(name)),
                                  mode="w")
    logfile.setFormatter(logformat)
    log = logging.getLogger(name)
    log.addHandler(logfile)
    return log
