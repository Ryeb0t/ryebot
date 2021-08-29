import os
from enum import Enum
from pathlib import Path

from ryebot.bot import PATHS
from ryebot.bot.cli.wiki_manager import LOGINCONTROLFILE, get_wiki_directory_from_name


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


    def register_command(self):
        """Clear the login control file, indicating that the command in there has been registered and executed."""

        with open(self.controlfile, 'w'):
            pass # empty the file


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
