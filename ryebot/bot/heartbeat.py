import time
import os

from ryebot.bot import PATHS


# File that will be edited by the daemon in a set interval, to prove that it is alive
HEARTBEATFILE = '.heartbeat'


def do_heartbeat():
    time.sleep(6)
    with open(os.path.join(PATHS['localdata'], HEARTBEATFILE), 'w') as f:
        f.write(time.strftime('%a, %d %b %Y %H:%M:%S')) # RFC5322 format
