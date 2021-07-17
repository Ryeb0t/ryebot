import logging
import os

from ryebot.bot import PATHS


LOGFORMAT = ('[%(asctime)s] [pid %(process)d tid %(thread)d (%(threadName)s)] %(message)s', '%a %b %d %H:%M:%S %Y')

# logfile for everything from the ryebotscript process
COMMONLOGFILE = '.log'

# logfile for all executed commands that started the ryebot module
COMMANDLOGFILE = '.cmdlog'

# logfile for every file system event
WATCHLOGFILE = '.watchlog'


def common_logger():
    filehandler = logging.FileHandler(os.path.join(PATHS['localdata'], COMMONLOGFILE))
    filehandler.setLevel(logging.INFO)
    filehandler.setFormatter(logging.Formatter(*LOGFORMAT))

    logger = logging.getLogger('common_logger')
    logger.addHandler(filehandler)

    return logger


def cmd_logger():
    filehandler = logging.FileHandler(os.path.join(PATHS['localdata'], COMMANDLOGFILE))
    filehandler.setLevel(logging.INFO)
    filehandler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', LOGFORMAT[1]))

    logger = logging.getLogger('cmd_logger')
    logger.addHandler(filehandler)

    return logger


def watchdog_logger():
    filehandler = logging.FileHandler(os.path.join(PATHS['localdata'], WATCHLOGFILE))
    filehandler.setLevel(logging.INFO)
    filehandler.setFormatter(logging.Formatter(*LOGFORMAT))

    logger = logging.getLogger('watchdog_logger')
    logger.addHandler(filehandler)

    return logger
