"""Entry script for the daemon process.

It turns the process with which is was started into the Ryebot daemon.
The `daemon_manager` module is used for running this script from the CLI.
"""

import os

from daemon import DaemonContext
from pid import PidFile

from ryebot.bot import PATHS
from ryebot.bot.monitorer import start_monitoring
from ryebot.bot.heartbeat import do_heartbeat


# File that contains the PID of the daemon; only exists while it is running
PIDFILE = '.ryebotd.pid'


def on_startup():
    # empty all control command files
    for dirpath, dirnames, filenames in os.walk(PATHS['localdata']):
        for filename in filenames:
            if filename.endswith('.control'):
                # empty the file
                try:
                    with open(filename, 'w'):
                        pass
                except OSError:
                    pass


def main():
    on_startup()
    start_monitoring(watchdog_logger(), common_logger())
    while True:
        do_heartbeat()


if __name__ == '__main__':
    with DaemonContext(pidfile=PidFile(PIDFILE, PATHS['localdata']), umask=0o022):
        from ryebot.bot.loggers import common_logger, watchdog_logger
        main()
