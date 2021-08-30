import logging
import time

from ryebot.bot.mgmt.logincontrol import LoginControl
from ryebot.bot.mgmt.loginstatus import ELoginStatus, LoginStatus
from ryebot.custom_utils.wiki_util import login_to_wiki as login


def login_to_wiki(wikiname: str, logger: logging.Logger):
    loginstatus = LoginStatus(wiki=wikiname)
    logincontrol = LoginControl(wiki=wikiname)

    loginstatus.status = ELoginStatus.LOGGING_IN

    try:
        # connect to wiki
        site, login_log = login(wikiname, return_log=True)
    except Exception as e:
        # connection failed
        loginstatus.status = ELoginStatus.LOGGED_OUT
        logger.info("Modified the login status file due to error while logging in.")
        logincontrol.register_command()
        raise e

    logger.info(login_log)

    # connection was successful
    loginstatus.status=ELoginStatus.LOGGED_IN
    loginstatus.last_login=time.time()
    logincontrol.register_command()