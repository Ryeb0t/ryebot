"""Implements the "heartbeat" functionality.

This includes writing the current time and date to a file every couple of
seconds, which proves that the daemon is still "alive" (i.e. running, its
"heart is beating").

The simple function `do_heartbeat` is called from the daemon's `main` function
in `ryebotd`.
"""

import os
import time

from ryebot.bot import PATHS


# File that will be edited by the daemon in a set interval, to prove that it is alive
HEARTBEATFILE = '.heartbeat'


def do_heartbeat():
    time.sleep(6)
    with open(os.path.join(PATHS['localdata'], HEARTBEATFILE), 'w') as f:
        f.write(time.strftime('%a, %d %b %Y %H:%M:%S')) # RFC5322 format
