import logging
import os
from enum import Enum
from pathlib import Path
import time

from ryebot.bot import PATHS
from ryebot.bot.cli.status_displayer import ELoginStatus
from ryebot.bot.cli.wiki_manager import LOGINSTATUSFILE, LOGINCONTROLFILE, get_wiki_directory_from_name
from ryebot.custom_utils.wiki_util import login_to_wiki as login


class ELoginControlCommand(Enum):
    DO_NOTHING = 0
    DO_LOGIN = 1
    DO_LOGOUT = 2
    UNKNOWN = 3

    def __str__(self):
        strmap = {
            'DO_NOTHING': '-',
            'DO_LOGIN': 'login',
            'DO_LOGOUT': 'logout',
            'UNKNOWN': '?'
        }
        return strmap[self.name]

    def __repr__(self):
        strmap = {
            'DO_NOTHING': 'Doing nothing',
            'DO_LOGIN': 'Logging in',
            'DO_LOGOUT': 'Logging out',
            'UNKNOWN': 'Unknown'
        }
        return strmap[self.name]


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


    @property
    def command(self):
        """Return the content of the login control file, as an `ELoginControlCommand` value."""

        # parse the size of the file
        filesize = os.stat(self.controlfile).st_size
        try:
            return ELoginControlCommand(int(filesize))
        except ValueError:
            # the file size is not in the enum's values,
            # so consider the control command to be unknown
            return ELoginControlCommand.UNKNOWN

    @command.setter
    def command(self, value: ELoginControlCommand):
        """Set the content of the wiki's login control file, indicating that the bot should login/logout there."""

        with open(self.controlfile, 'w') as f:
            if value == ELoginControlCommand.DO_LOGIN:
                f.write('1')
            elif value == ELoginControlCommand.DO_LOGOUT:
                f.write('11')


class LoginStatus():
    """Class for reading and modifying the login status file of a wiki."""

    def __init__(self, wiki: str='', file: str=''):
        """Access the login status file of a wiki, either using the wiki name or the file name directly."""

        if file:
            self.statusfile = file
        elif wiki:
            self.statusfile = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wiki), LOGINSTATUSFILE)
        else:
            raise ValueError('LoginStatus requires either a wiki name or a file name!')

        if not os.path.exists(self.statusfile):
            Path(self.statusfile).touch() # create the file

        # read current lines in the file
        with open(self.statusfile) as f:
            lines = f.readlines()

        for _ in range(3-len(lines)):
            # if the file has fewer than three lines, then append the missing number of lines
            lines.append('\n')


    def _modify_line(self, linenumber: int, new_linecontent: str):
        """Change the content of a line in the status file."""

        # read current lines in the file
        with open(self.statusfile) as f:
            lines = f.readlines()

        # modify the relevant line
        lines[linenumber] = new_linecontent

        # write modified lines to file
        with open(self.statusfile, 'w+') as f:
            f.writelines(lines)


    @property
    def status(self):
        """Return the current login status, as an `ELoginStatus` value."""

        with open(self.statusfile) as f:
            try:
                line = f.readline().strip() # first line in the file
                return ELoginStatus(int(line))
            except (IndexError, ValueError):
                # reading the first line might have failed,
                # or conversion to int/LoginStatus might have failed,
                # so consider the status to be unknown
                return ELoginStatus.UNKNOWN

    @status.setter
    def status(self, value: ELoginStatus):
        """Set the "status" part of the login status file."""

        self._modify_line(0, str(value.value) + '\n')


    @property
    def last_login(self):
        """Return the time of last login, as a `struct_time` value."""

        with open(self.statusfile) as f:
            try:
                f.readline()
                line = f.readline().strip() # second line in the file
                return time.gmtime(float(line))
            except ValueError:
                # reading the second line might have failed,
                # or conversion to float might have failed,
                # so return the default Jan 1, 1970
                return time.gmtime(0)

    @last_login.setter
    def last_login(self, value: float):
        """Set the "last_login" part of the login status file."""

        self._modify_line(1, str(value) + '\n')


    @property
    def last_logout(self):
        """Return the time of last logout, as a `struct_time` value."""

        with open(self.statusfile) as f:
            try:
                f.readline()
                f.readline()
                line = f.readline().strip() # third line in the file
                return time.gmtime(float(line))
            except ValueError:
                # reading the third line might have failed,
                # or conversion to float might have failed,
                # so return the default Jan 1, 1970
                return time.gmtime(0)

    @last_logout.setter
    def last_logout(self, value: float):
        """Set the "last_logout" part of the login status file."""

        self._modify_line(2, str(value))


    @property
    def all_info(self):
        """Return a tuple of the current status and the time of last login and logout."""

        all_info = []

        with open(self.statusfile) as f:
            status = f.readline().strip()
            last_login = f.readline().strip()
            last_logout = f.readline().strip()

        try:
            all_info.append(ELoginStatus(int(status)))
        except ValueError:
            all_info.append(ELoginStatus.UNKNOWN)
        try:
            all_info.append(time.gmtime(float(last_login)))
        except ValueError:
            all_info.append(time.gmtime(0))
        try:
            all_info.append(time.gmtime(float(last_logout)))
        except ValueError:
            all_info.append(time.gmtime(0))

        return tuple(all_info)



def login_to_wiki(wikiname: str, logger: logging.Logger):
    _modify_loginstatus_file(logger, wikiname, newstatus=ELoginStatus.LOGGING_IN)

    try:
        site, login_log = login(wikiname, return_log=True)
    except Exception as e:
        _modify_loginstatus_file(logger, wikiname, newstatus=ELoginStatus.LOGGED_OUT)
        logger.info("Modified the login status file due to error while logging in.")
        _register_control_command(wikiname)
        raise e

    logger.info(login_log)
    _modify_loginstatus_file(logger, wikiname, newstatus=ELoginStatus.LOGGED_IN, newlastlogin=time.time())
    _register_control_command(wikiname)


def _modify_loginstatus_file(logger: logging.Logger, wiki: str, newstatus: ELoginStatus=None, newlastlogin: float=None, newlastlogout: float=None):
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