import importlib
import logging
import os
import sys

from ryebot.bot.ryebotd import LOGFILE
from ryebot.bot import PATHS


def main():
    try:
        scriptname = sys.argv[1]
    except IndexError:
        return

    logging.basicConfig(level=logging.INFO, filename=os.path.join(PATHS['localdata'], LOGFILE),
        format='[%(asctime)s] [pid %(process)d tid %(thread)d] %(message)s', datefmt='%a %b %d %H:%M:%S %Y')

    if scriptname == '_login':
        from .login_and_logout import login_to_wiki
        login_to_wiki()
    else:
        scriptmodule = importlib.import_module(scriptname)
        scriptmodule.main()


if __name__ == '__main__':
    main()
