import logging
import os
import psutil

from ryebot.bot import PATHS
from ryebot.bot.cli.wiki_manager import LOGINCONTROLFILE, LOGINSTATUSFILE, get_wiki_name_from_directory, get_wiki_directory_from_path
from ryebot.bot.cli.status_displayer import LoginControlCommand, LoginStatus


class FileModifiedEventHandler():

    def __init__(self, logger: logging.Logger, file_path: str):
        self.logger = logger
        self.file_path = file_path


    def handle(self):
        # a file was modified, so the daemon is supposed to do something.
        # we use the following methods to find out what that is, based on the file path, content, size, etc.

        # command to go online or offline on a wiki
        self._logincontrolcommand()

        # login or logout completed, so start/stop pingchecker
        self._pingchecker()


    def _logincontrolcommand(self):
        if os.path.basename(self.file_path) != LOGINCONTROLFILE:
            return
        if os.path.dirname(os.path.dirname(os.path.dirname(self.file_path))) != PATHS['wikis']:
            return

        # parse the size of the file
        filesize = os.stat(self.file_path).st_size
        try:
            newstatus = LoginControlCommand(int(filesize))
        except ValueError:
            # the file size is not in the enum's values, so consider the control command invalid
            return
        if newstatus == LoginControlCommand.DO_NOTHING:
            return

        wikidir, wikisubdir = get_wiki_directory_from_path(self.file_path)

        wikiname = get_wiki_name_from_directory(wikidir, wikisubdir)
        self.logger.info(f'{repr(newstatus)} on the "{wikiname}" wiki.')

        if newstatus == LoginControlCommand.DO_LOGIN:
            python_command = os.path.join(PATHS['venv'], 'bin', 'python3')
            script_file = os.path.join(PATHS['package'], 'bot', 'ryebotscript.py')
            wikidirectory = os.path.join(PATHS['wikis'], wikidir, wikisubdir)
            psutil.Popen([python_command, script_file, '_login'], cwd=wikidirectory)
            self.logger.info('Started new Python process for logging in.')


    def _pingchecker(self):
        if os.path.basename(self.file_path) != LOGINSTATUSFILE:
            return
        if os.path.dirname(os.path.dirname(os.path.dirname(self.file_path))) != PATHS['wikis']:
            return

        # parse the size of the file
        filesize = os.stat(self.file_path).st_size
        try:
            loginstatus = LoginStatus(int(filesize))
        except ValueError:
            # the file size is not in the enum's values, so consider the login status invalid
            return
        if loginstatus == LoginStatus.LOGGING_IN:
            return

        wikidir, wikisubdir = get_wiki_directory_from_path(self.file_path)

        wikiname = get_wiki_name_from_directory(wikidir, wikisubdir)
        self.logger.info(f'{"Starting" if loginstatus == LoginStatus.LOGGED_IN else "Stopping"} the pingchecker on the "{wikiname}" wiki.')

        if loginstatus == LoginStatus.LOGGED_IN:
            # start the pingchecker
            python_command = os.path.join(PATHS['venv'], 'bin', 'python3')
            script_file = os.path.join(PATHS['package'], 'bot', 'ryebotscript.py')
            wikidirectory = os.path.join(PATHS['wikis'], wikidir, wikisubdir)
            psutil.Popen([python_command, script_file, '_pingchecker'], cwd=wikidirectory)
            self.logger.info('Started new Python process for starting the pingchecker.')
        else:
            # stop the pingchecker
            pass
