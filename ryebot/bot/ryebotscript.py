"""Entry script for running a wiki script.

It is called from the `daemon_handlers` module, and includes the "meta scripts"
for logging in or out and starting the pingchecker. Depending on which script
is to be run, it imports that script's module and runs its main function.
"""

import importlib
import os
import sys

from ryebot.bot.loggers import common_logger
from ryebot.bot.utils import get_wiki_name_from_path


def main():
    logger = common_logger()

    wikiname = get_wiki_name_from_path(os.getcwd())

    try:
        logger.info(f'Starting the "{sys.argv[1]}" script on the "{wikiname}" wiki.')
        scriptname = sys.argv[1]
    except IndexError:
        # no script name specified
        return

    # wrapper for script execution, catch errors thrown by the script
    try:
        # import script and run it
        # special scripts:
        if scriptname == '_login':
            from ryebot.bot.mgmt.login_and_logout import login_to_wiki
            login_to_wiki(wikiname, logger)
        elif scriptname == '_pingchecker':
            from ryebot.bot.pingchecker import pingcheck
            pingcheck(wikiname, logger)

        # common scripts:
        else:
            scriptmodule = importlib.import_module(scriptname)
            scriptmodule.main()

    except Exception:
        logstr = f'Error during the "{sys.argv[1]}" script on the "{wikiname}" wiki!'
        logger.info(logstr, exc_info=True, stack_info=True)


if __name__ == '__main__':
    main()
