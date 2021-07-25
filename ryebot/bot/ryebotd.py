import os
import time

from daemon import DaemonContext
from pid import PidFile

from ryebot.bot import PATHS
from ryebot.bot.monitorer import start_monitoring


# File that will be edited by the daemon in a set interval, to prove that it is alive
HEARTBEATFILE = '.heartbeat'

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


def do_heartbeat():
    time.sleep(6)
    with open(os.path.join(PATHS['localdata'], HEARTBEATFILE), 'w') as f:
        f.write(time.strftime('%a, %d %b %Y %H:%M:%S')) # RFC5322 format


def main():
    on_startup()
    start_monitoring(watchdog_logger(), common_logger())
    while True:
        do_heartbeat()


if __name__ == '__main__':
    with DaemonContext(pidfile=PidFile(PIDFILE, PATHS['localdata']), umask=0o022):
        from ryebot.bot.loggers import common_logger, watchdog_logger
        main()
