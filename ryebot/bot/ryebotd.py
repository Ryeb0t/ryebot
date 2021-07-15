import logging
import os
import time

from daemon import DaemonContext

from ryebot.bot import PATHS


LOGFILE = '.log'


def maind():
    logging.basicConfig(level=logging.INFO, filename=os.path.join(PATHS['localdata'], LOGFILE), format='[%(asctime)s] [pid %(pid)d] %(message)s', datefmt='%a %b %d %H:%M:%S %Y')
    while True:
        time.sleep(6)
        logging.info('heartbeat from daemon', extra={'pid': os.getpid()})


def main():
    with DaemonContext():
        maind()


if __name__ == '__main__':
    main()