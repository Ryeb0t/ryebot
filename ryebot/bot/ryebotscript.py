import importlib
import os
import sys

from ryebot.bot import PATHS
from ryebot.bot.loggers import common_logger


def main():
    try:
        scriptname = sys.argv[1]
    except IndexError:
        return

    logger = common_logger()

    if scriptname == '_login':
        from .login_and_logout import login_to_wiki
        login_to_wiki()
    else:
        scriptmodule = importlib.import_module(scriptname)
        scriptmodule.main()


if __name__ == '__main__':
    main()
