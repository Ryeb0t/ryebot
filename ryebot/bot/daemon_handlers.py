import logging
import os
import psutil

from ryebot.bot import PATHS
from ryebot.bot.cli.wiki_manager import LOGINCONTROLFILE
from ryebot.bot.cli.status_displayer import LoginControlCommand


class FileModifiedEventHandler():

    def __init__(self, logger: logging.Logger, file_path: str):
        self.logger = logger
        self.file_path = file_path

    def handle(self):
        # a file was modified, so the daemon is supposed to do something.
        # we use the following methods to find out what that is, based on the file path, content, size, etc.

        # command to go online or offline on a wiki
        self.logincontrolcommand()


    def logincontrolcommand(self):
        if os.path.basename(self.file_path) != LOGINCONTROLFILE:
            return
        if os.path.dirname(os.path.dirname(self.file_path)) != PATHS['wikis']:
            return
        
        filesize = os.stat(self.file_path).st_size
        try:
            newstatus = LoginControlCommand(int(filesize))
        except ValueError:
            # the file size is not in the enum's values, so consider the control command invalid
            return
        if newstatus == LoginControlCommand.DO_NOTHING:
            return

        wikiname = os.path.basename(os.path.dirname(self.file_path))

        self.logger.info(f'{str(newstatus)} on the "{wikiname}" wiki.')

        if newstatus == LoginControlCommand.DO_LOGIN:
            python_command = os.path.join(PATHS['venv'], 'bin', 'python3')
            script_file = os.path.join(PATHS['package'], 'bot', 'ryebotscript.py')
            wikidirectory = os.path.join(PATHS['wikis'], wikiname)
            psutil.Popen([python_command, script_file, '_login'], cwd=wikidirectory)
            self.logger.info('Started new Python process for logging in.')
