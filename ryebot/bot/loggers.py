import logging
import os

from ryebot.bot import PATHS


LOGFORMAT = ('[%(asctime)s] '
    '[pid %(process)d tid %(thread)d (%(threadName)s)] '
    '%(message)s',
    '%a %b %d %H:%M:%S %Y')

# logfile for everything from the ryebotscript process
COMMONLOGFILE = '.log'

# logfile for all executed commands that started the ryebot module
COMMANDLOGFILE = '.cmdlog'

# logfile for every file system event
WATCHLOGFILE = '.watchlog'


def _make_logger(name: str='', handler: logging.Handler=None):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        # if the logger has handlers, then this function was already called for this logger.
        # in that case, don't add the handler again
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    return logger


def common_logger():
    filehandler = logging.FileHandler(os.path.join(PATHS['localdata'], COMMONLOGFILE))
    filehandler.setFormatter(logging.Formatter(*LOGFORMAT))
    return _make_logger('common_logger', filehandler)


def cmd_logger():
    filehandler = logging.FileHandler(os.path.join(PATHS['localdata'], COMMANDLOGFILE))
    filehandler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', LOGFORMAT[1]))
    return _make_logger('cmd_logger', filehandler)


def watchdog_logger():
    filehandler = logging.FileHandler(os.path.join(PATHS['localdata'], WATCHLOGFILE))
    filehandler.setFormatter(logging.Formatter(*LOGFORMAT))
    return _make_logger('watchdog_logger', filehandler)
