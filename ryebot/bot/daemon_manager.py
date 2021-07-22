import os

import psutil
from pid import PidFile, PidFileAlreadyRunningError

from ryebot.bot import PATHS
from ryebot.bot.loggers import cmd_logger
from ryebot.bot.ryebotd import PIDFILE


def _is_daemon_already_running():
    try:
        PidFile(PIDFILE, PATHS['localdata']).check()
        # if the check() method succeeded without an error, then the daemon
        # is currently not running normally
        return False
    except PidFileAlreadyRunningError:
        return True


    running_daemons = find_procs_by_cmd('ryebotd.py')
    return len(running_daemons) > 0


def start_daemon():
    if _is_daemon_already_running():
        return
    python_command = os.path.join(PATHS['venv'], 'bin', 'python3')
    daemon_file = os.path.join(PATHS['package'], 'bot', 'ryebotd.py')
    psutil.Popen([python_command, daemon_file])


def log_command(command):
    cmd_logger().info(command)
