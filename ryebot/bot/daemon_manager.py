import logging
import os

import psutil

from ryebot.bot import PATHS
from ryebot.custom_utils.ps_util import find_procs_by_name


# file that stores a log of all entered commands
COMMANDLOGFILE = '.cmdlog'


def _is_daemon_already_running():
    running_daemons = find_procs_by_name('ryebotd.py')
    return len(running_daemons) > 0


def start_daemon():
    if _is_daemon_already_running():
        return
    cmd = os.path.join(PATHS['venv'], 'bin', 'python3')
    psutil.Popen([cmd, 'ryebotd.py'])


def log_command(command):
    logging.basicConfig(level=logging.INFO, filename=os.path.join(PATHS['localdata'], COMMANDLOGFILE), format='[%(asctime)s] %(message)s', datefmt='%a %b %d %H:%M:%S %Y')
    logging.info(command)
