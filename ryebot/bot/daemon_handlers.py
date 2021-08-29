import logging
import os

from pid import PidFile, PidFileAlreadyRunningError
import psutil

from ryebot.bot import PATHS
from ryebot.bot.cli.wiki_manager import LOGINCONTROLFILE, LOGINSTATUSFILE, get_wiki_directory_from_name, get_wiki_name_from_directory, get_wiki_directory_from_path
from ryebot.bot.logincontrol import ELoginControlCommand, LoginControl
from ryebot.bot.loginstatus import ELoginStatus, LoginStatus
from ryebot.bot.pingchecker import PIDFILE


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

        controlcommand = LoginControl(file=self.file_path).command
        if controlcommand in (ELoginControlCommand.DO_NOTHING, ELoginControlCommand.UNKNOWN):
            return

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
            return
        if os.path.dirname(os.path.dirname(os.path.dirname(self.file_path))) != PATHS['wikis']:
            return

        loginstatus = LoginStatus(file=self.file_path).status
        if loginstatus in (ELoginStatus.LOGGING_IN, ELoginStatus.UNKNOWN):
            return

        wikidir, wikisubdir = get_wiki_directory_from_path(self.file_path)

        wikiname = get_wiki_name_from_directory(wikidir, wikisubdir)
        self.logger.info(f'{"Starting" if loginstatus == ELoginStatus.LOGGED_IN else "Stopping"} the pingchecker on the "{wikiname}" wiki.')

        if loginstatus == ELoginStatus.LOGGED_IN:
            # start the pingchecker
            python_command = os.path.join(PATHS['venv'], 'bin', 'python3')
            script_file = os.path.join(PATHS['package'], 'bot', 'ryebotscript.py')
            wikidirectory = os.path.join(PATHS['wikis'], wikidir, wikisubdir)
            p = psutil.Popen([python_command, script_file, '_pingchecker'], cwd=wikidirectory)
            self.logger.info(f'Started new Python process with PID {p.pid} for starting the pingchecker.')
        else:
            # stop the pingchecker
            pidfiledir = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wikiname))
            try:
                check_result = PidFile(pidname=PIDFILE, piddir=pidfiledir).check()
                # if the check() method succeeded without an error, then the process
                # is currently not running normally, so there's no need to terminate it
                self.logger.info(f'The ping checker is currently not running normally (check result: "{check_result}"), so leaving it be.')
            except PidFileAlreadyRunningError as e:
                # process is running normally, so we can terminate it without problems.
                # conveniently, the error object has an attribute with the PID stored in the PID file
                psutil.Process(e.pid).terminate()
                self.logger.info(f'Terminated the ping checker process successfully (PID was {e.pid}).')
