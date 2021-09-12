"""Provides the "pingcheck" functionality to respond to ping requests.

Wiki editors can edit a specific page on the wiki to make a "ping request"
and check if the bot is online. If it is, it edits that page too, as a
"ping response".

The entry function is `pingcheck`, it starts an infinite loop where the
ping request page is checked every couple of seconds.
"""

import logging
import os
import time

from pid import PidFile

from ryebot.bot import PATHS
from ryebot.bot.mgmt.loginstatus import LoginStatus
from ryebot.bot.utils import get_wiki_directory_from_name, login
from ryebot.custom_utils.time_util import format_secs
from ryebot.custom_mwclient.fandom_client import FandomClient


# seconds to wait between subsequent checks of the ping page
PERIOD = 7

# file that contains the PID of the pingchecker process; only exists while it is running
PIDFILE = '.pingchecker.pid'

PINGPAGE = 'User:{username}/bot/ping'
PINGPAGETEXT = (
    'Use this page to verify my online status. '
    "If I'm online, I will respond within a couple of seconds!"
)
TIME_UNTIL_WIPE = 90
WIPE_SUMMARY = 'Wiped.'
RESPONSE_SUMMARY = 'Ping response.'
RESPONSE_TEXT = (
    '\n\nOnline. Time of startup: {startuptime}. --~~~~\n\n'
    'Will wipe this page shortly...'
)


def pingcheck(wikiname: str, logger: logging.Logger):

    # create a PID file to make it easy to kill this process (e.g. when logging out)
    pidfiledir = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wikiname))
    with PidFile(pidname=PIDFILE, piddir=pidfiledir):

        # login to wiki
        try:
            site, login_log = login(wikiname, return_log=True)
        except Exception as err:
            logger.info(
                f'Failed to login to the "{wikiname}" wiki in order to'
                'start the pingchecker.'
            )
            raise err

        logger.info(login_log)
        logger.info(f'Started pingchecker on the "{wikiname}" wiki.')

        pingpage_name = PINGPAGE.format(username=site.get_current_wiki_user())

        # remember the content of the ping page as it is right now when starting the pingchecker
        initial_pingpage_text = site.client.pages[pingpage_name].text()

        # get time of formal login to wiki, for the ping responses
        startuptime = LoginStatus(wiki=wikiname).last_login
        if not startuptime:
            startuptime = '(unknown)'
        else:
            startuptime = format_secs(startuptime)

        # start listening
        while True:
            time.sleep(PERIOD)
            _check(site, pingpage_name, initial_pingpage_text, startuptime)


def _check(site: FandomClient, pingpage_name: str, initial_pingpage_text: str, startuptime: float):
    pingpage = site.client.pages[pingpage_name]
    pingpage_text = pingpage.text()

    if pingpage_text != PINGPAGETEXT:
        # current text is different from what we expect
        if '(UTC)' in pingpage_text:
            # there is a ping request in the current text
            if pingpage_text != initial_pingpage_text:
                # and is this also a fresh request, not one from before we started the pingchecker.
                # therefore, prepare the response
                page_new_text = pingpage_text + (RESPONSE_TEXT.format(startuptime=startuptime))
                # publish the response
                site.save(pingpage, page_new_text, summary=RESPONSE_SUMMARY, minor=True)
                # wait a bit
                time.sleep(TIME_UNTIL_WIPE)
                # and wipe all requests
                site.save(pingpage, PINGPAGETEXT, summary=WIPE_SUMMARY, minor=True)
        else:
            # deviation from expected text, but not a ping request.
            # therefore, just wipe to reset to expected text
            site.save(pingpage, PINGPAGETEXT, WIPE_SUMMARY, minor=True)
