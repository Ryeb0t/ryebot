import logging
import os
from pathlib import Path
import time

from ryebot.bot import PATHS
from ryebot.bot.cli.status_displayer import LoginControlCommand, LoginStatus
from ryebot.bot.cli.wiki_manager import LOGINSTATUSFILE, LOGINCONTROLFILE, get_wiki_directory_from_name
from ryebot.custom_utils.wiki_util import login_to_wiki as login


class LoginControl():
    """Class for reading and modifying the login control file of a wiki."""

    def __init__(self, wiki: str='', file: str=''):
        """Access the login control file of a wiki, either using the wiki name or the file name directly."""

        if file:
            self.controlfile = file
        elif wiki:
            self.controlfile = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wiki), LOGINCONTROLFILE)
        else:
            raise ValueError('LoginControl requires either a wiki name or a file name!')
        
        if not os.path.exists(self.controlfile):
            Path(self.controlfile).touch() # create the file


    def command_login(self):
        """Set the content of the wiki's login control file size to 1, indicating that the bot should login there."""

        with open(self.controlfile, 'w') as f:
            f.write('1')


    def command_logout(self):
        """Set the content of the wiki's login control file size to 2, indicating that the bot should logout there."""

        with open(self.controlfile, 'w') as f:
            f.write('11')


    @property
    def command(self):
        """Return the content of the login control file, as a `LoginControlCommand` value."""
        
        # parse the size of the file
        filesize = os.stat(self.controlfile).st_size
        try:
            return LoginControlCommand(int(filesize))
        except ValueError:
            # the file size is not in the enum's values,
            # so consider the control command to be "do nothing"
            return LoginControlCommand.DO_NOTHING



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
    loginstatusfile = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wiki), LOGINSTATUSFILE)
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
    logincontrolfile = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wiki), LOGINCONTROLFILE)
    # empty the file
    with open(logincontrolfile, 'w'):
        pass