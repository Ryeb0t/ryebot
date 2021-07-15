import logging
import os
import time

from daemon import DaemonContext
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

from ryebot.bot import PATHS


LOGFILE = '.log'


def start_monitoring():
    monitored_directory = PATHS['localdata']
    observer = Observer()
    observer.schedule(LoggingEventHandler(), monitored_directory, recursive=True)
    observer.start()


def maind():
    logging.basicConfig(level=logging.INFO, filename=os.path.join(PATHS['localdata'], LOGFILE),
        format='[%(asctime)s] [pid %(pid)d] %(message)s', datefmt='%a %b %d %H:%M:%S %Y')

    start_monitoring()

    while True:
        time.sleep(6)
        logging.info('heartbeat from daemon', extra={'pid': os.getpid()})


def main():
    with DaemonContext():
        maind()


if __name__ == '__main__':
    main()