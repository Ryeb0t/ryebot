import os

import psutil
from pid import PidFile, PidFileAlreadyRunningError

from ryebot.bot import PATHS
from ryebot.bot.ryebotd import PIDFILE


def _is_daemon_already_running():
    try:
        PidFile(PIDFILE, PATHS['localdata']).check()
        # if the check() method succeeded without an error, then the daemon
        # is currently not running normally
        return False
    except PidFileAlreadyRunningError:
        return True


def _run_daemon():
    python_executable = os.path.join(PATHS['venv'], 'bin', 'python3')
    daemon_pythonfile = os.path.join(PATHS['package'], 'bot', 'ryebotd.py')

    # start a new process that runs the ryebotd.py file with the Python interpreter of the venv;
    # the last argument is not functional, it's just for easily identifying the process
    psutil.Popen([python_executable, daemon_pythonfile, 'ryebotd'])


def start_daemon():
    if not _is_daemon_already_running():
        _run_daemon()
