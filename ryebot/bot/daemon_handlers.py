import logging
import os

from pid import PidFile, PidFileAlreadyRunningError
import psutil

from ryebot.bot import PATHS
from ryebot.bot.mgmt.logincontrol import ELoginControlCommand, LoginControl, LOGINCONTROLFILE
from ryebot.bot.mgmt.loginstatus import ELoginStatus, LoginStatus, LOGINSTATUSFILE
from ryebot.bot.pingchecker import PIDFILE
from ryebot.bot.utils import (get_wiki_directory_from_name,
    get_wiki_directory_from_path, get_wiki_name_from_directory)


class FileModifiedEventHandler():
    """Class that starts new processes, depending on the file that was modified."""

    def __init__(self, logger: logging.Logger, file_path: str):
        self.logger = logger
        self.file_path = file_path


    def handle(self):
        """Entry function, contains all methods for starting new processes."""

        # a file was modified, so the daemon is supposed to do something.
        # we use the following methods to find out what that is,
        # based on the file path, content, size, etc.

        # command to go online or offline on a wiki
        self._logincontrolcommand()

        # login or logout completed, so start/stop pingchecker
        self._pingchecker()


    def _logincontrolcommand(self):
        if os.path.basename(self.file_path) != LOGINCONTROLFILE:
            # file must be the login control file
            return
        if os.path.dirname(os.path.dirname(os.path.dirname(self.file_path))) != PATHS['wikis']:
            # file must be in the wikis directory
            return

        controlcommand = LoginControl(file=self.file_path).command
        if controlcommand not in (ELoginControlCommand.DO_LOGIN, ELoginControlCommand.DO_LOGOUT):
            # login control command must be login/logout
            return

        # all checks passed

        wikidir, wikisubdir = get_wiki_directory_from_path(self.file_path)

        wikiname = get_wiki_name_from_directory(wikidir, wikisubdir)
        self.logger.info(f'{repr(controlcommand)} on the "{wikiname}" wiki.')

        if controlcommand == ELoginControlCommand.DO_LOGIN:
            python_command = os.path.join(PATHS['venv'], 'bin', 'python3')
            script_file = os.path.join(PATHS['package'], 'bot', 'ryebotscript.py')
            wikidirectory = os.path.join(PATHS['wikis'], wikidir, wikisubdir)
            p = psutil.Popen([python_command, script_file, '_login'], cwd=wikidirectory)
            self.logger.info(f'Started new Python process with PID {p.pid} for logging in.')


    def _pingchecker(self):
        if os.path.basename(self.file_path) != LOGINSTATUSFILE:
            # file must be the login status file
            return
        if os.path.dirname(os.path.dirname(os.path.dirname(self.file_path))) != PATHS['wikis']:
            # file must be in the wikis directory
            return

        loginstatus = LoginStatus(file=self.file_path).status
        if loginstatus not in (ELoginStatus.LOGGED_IN, ELoginStatus.LOGGED_OUT):
            # login status must be logged in/out
            return

        # all checks passed

        wikidir, wikisubdir = get_wiki_directory_from_path(self.file_path)

        wikiname = get_wiki_name_from_directory(wikidir, wikisubdir)
        logstr = '{action} the pingchecker on the "{wiki}" wiki.'.format(
            action="Starting" if loginstatus == ELoginStatus.LOGGED_IN else "Stopping",
            wiki=wikiname)
        self.logger.info(logstr)

        if loginstatus == ELoginStatus.LOGGED_IN:
            # start the pingchecker
            python_command = os.path.join(PATHS['venv'], 'bin', 'python3')
            script_file = os.path.join(PATHS['package'], 'bot', 'ryebotscript.py')
            wikidirectory = os.path.join(PATHS['wikis'], wikidir, wikisubdir)
            p = psutil.Popen([python_command, script_file, '_pingchecker'], cwd=wikidirectory)
            self.logger.info(f'Started new Python process with PID {p.pid}'
                'for starting the pingchecker.')
        else:
            # stop the pingchecker
            pidfiledir = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wikiname))
            try:
                check_result = PidFile(pidname=PIDFILE, piddir=pidfiledir).check()
                # if the check() method succeeded without an error, then the process
                # is currently not running normally, so there's no need to terminate it
                self.logger.info('The ping checker is currently not running '
                    f'normally (check result: "{check_result}"), so leaving it be.')
            except PidFileAlreadyRunningError as e:
                # process is running normally, so we can terminate it without problems.
                # conveniently, the error object has an attribute with the PID
                # stored in the PID file
                psutil.Process(e.pid).terminate()
                self.logger.info('Terminated the ping checker process successfully '
                    f'(PID was {e.pid}).')
