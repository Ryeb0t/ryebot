import logging
import os
from pathlib import Path
import time

from ryebot.bot import PATHS
from ryebot.bot.cli.status_displayer import LoginStatus
from ryebot.bot.cli.wiki_manager import LOGINSTATUSFILE, LOGINCONTROLFILE
from ryebot.custom_utils.wiki_util import login_to_wiki as login


def login_to_wiki(wikiname: str, logger: logging.Logger):
    _modify_loginstatus_file(logger, wikiname, newstatus=LoginStatus.LOGGING_IN)

    try:
        site, login_log = login(wikiname, return_log=True)
    except Exception as e:
        _modify_loginstatus_file(logger, wikiname, newstatus=LoginStatus.LOGGED_OUT)
        logger.info("Modified the login status file due to error while logging in.")
        _register_control_command(wikiname)
        raise e

    logger.info(login_log)
    _modify_loginstatus_file(logger, wikiname, newstatus=LoginStatus.LOGGED_IN, newlastlogin=time.time())
    _register_control_command(wikiname)


def _modify_loginstatus_file(logger: logging.Logger, wiki: str, newstatus: LoginStatus=None, newlastlogin: float=None, newlastlogout: float=None):
    loginstatusfile = os.path.join(PATHS['wikis'], wiki, LOGINSTATUSFILE)
    if not os.path.exists(loginstatusfile):
        Path(loginstatusfile).touch() # create the file

    lines = []

    # read current lines in the file
    with open(loginstatusfile) as f:
        lines = f.readlines()

    for _ in range(3-len(lines)):
        # if the file has fewer than three lines, then append the missing number of lines
        lines.append('\n')

    # modify the lines
    if newstatus:
        lines[0] = str(newstatus.value) + '\n'
    if newlastlogin:
        lines[1] = str(newlastlogin) + '\n'
    if newlastlogout:
        lines[2] = str(newlastlogout)

    # write modified lines to file
    with open(loginstatusfile, 'w+') as f:
        f.writelines(lines)


def _register_control_command(wiki: str):
    logincontrolfile = os.path.join(PATHS['wikis'], wiki, LOGINCONTROLFILE)
    # empty the file
    with open(logincontrolfile, 'w'):
        pass