import os
from enum import Enum
from pathlib import Path

from ryebot.bot import PATHS
from ryebot.bot.utils import get_wiki_directory_from_name


# Name of the file that holds the login status for the wiki.
# This file contains three lines: 1) the status (0 - logged out,
# 1 - logging in, 2 - logged in), 2) the time of the last successful
# login, and 3) the time of the last logout. Both times are in
# seconds since the Unix epoch.
LOGINSTATUSFILE = '.login.status'


class ELoginStatus(Enum):
    LOGGED_OUT = 0
    LOGGING_IN = 1
    LOGGED_IN = 2
    UNKNOWN = 3

    def __str__(self):
        strmap = {
            'LOGGED_OUT': 'logged out',
            'LOGGING_IN': 'logging in',
            'LOGGED_IN': 'logged in',
            'UNKNOWN': 'unknown'
        }
        return strmap[self.name]


class LoginStatus():
    """Class for reading and modifying the login status file of a wiki."""

    def __init__(self, wiki: str = '', file: str = ''):
        """Access the login status file of a wiki.

        This is possible either using the wiki name or the file name directly.
        """

        if file:
            self.statusfile = file
        elif wiki:
            self.statusfile = os.path.join(PATHS['wikis'],
                *get_wiki_directory_from_name(wiki), LOGINSTATUSFILE)
        else:
            raise ValueError('LoginStatus requires either a wiki name or a file name!')

        if not os.path.exists(self.statusfile):
            Path(self.statusfile).touch() # create the file


    def _modify_line(self, linenumber: int, new_linecontent: str):
        """Change the content of a line in the status file."""

        # read current lines in the file
        with open(self.statusfile) as f:
            lines = f.readlines()

        for _ in range(3-len(lines)):
            # if the file has fewer than three lines, then append the missing number of lines
            lines.append('\n')

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
        """Return the time of last login, as a float value."""

        with open(self.statusfile) as f:
            try:
                f.readline()
                line = f.readline().strip() # second line in the file
                return float(line)
            except ValueError:
                # reading the second line might have failed,
                # or conversion to float might have failed,
                # so return the default Jan 1, 1970
                return 0.0

    @last_login.setter
    def last_login(self, value: float):
        """Set the "last_login" part of the login status file."""

        self._modify_line(1, str(value) + '\n')


    @property
    def last_logout(self):
        """Return the time of last logout, as a float value."""

        with open(self.statusfile) as f:
            try:
                f.readline()
                f.readline()
                line = f.readline().strip() # third line in the file
                return float(line)
            except ValueError:
                # reading the third line might have failed,
                # or conversion to float might have failed,
                # so return the default Jan 1, 1970
                return 0.0

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
            all_info.append(float(last_login))
        except ValueError:
            all_info.append(0.0)
        try:
            all_info.append(float(last_logout))
        except ValueError:
            all_info.append(0.0)

        return tuple(all_info)
