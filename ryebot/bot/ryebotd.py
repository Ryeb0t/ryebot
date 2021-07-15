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
    logging.info(f'Now listening to all changes to the "{monitored_directory}" directory and its subdirectories, recursively.')
    observer.start()


def maind():
    logging.basicConfig(level=logging.INFO, filename=os.path.join(PATHS['localdata'], LOGFILE),
        format='[%(asctime)s] [pid %(pid)d] %(message)s', datefmt='%a %b %d %H:%M:%S %Y')

    # TODO: Create a custom subclass of watchdog.observers.Observer that excludes the logfile, as we get an infinite logging loop otherwise.
    # It should also include the "extra" directory with the pid when calling logging.info, since the logging fails silently otherwise.
    #start_monitoring()

    while True:
        time.sleep(6)
        logging.info('heartbeat from daemon', extra={'pid': os.getpid()})


def main():
    with DaemonContext():
        maind()


if __name__ == '__main__':
    main()