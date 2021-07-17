import os

import psutil

from ryebot.bot import PATHS
from ryebot.custom_utils.ps_util import find_procs_by_cmd
from ryebot.bot.loggers import cmd_logger


def _is_daemon_already_running():
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
