import logging
import os
import psutil

from ryebot.bot import PATHS
from ryebot.bot.wiki_manager import ONLINESTATUSFILENAME
from ryebot.bot.status_displayer import OnlineStatus


class FileModifiedEventHandler():

    def __init__(self, logger: logging.Logger, file_path: str):
        self.logger = logger
        self.file_path = file_path

    def handle(self):
        # a file was modified, so the daemon is supposed to do something.
        # we use the following methods to find out what that is, based on the file path, content, size, etc.

        # changes to the online status on a wiki
        self.onlinestatus()


    def onlinestatus(self):
        if os.path.basename(self.file_path) != ONLINESTATUSFILENAME:
            return
        if os.path.dirname(os.path.dirname(self.file_path)) != PATHS['wikis']:
            return

        wikiname = os.path.basename(os.path.dirname(self.file_path))
        if os.stat(self.file_path).st_size > 0:
            newstatus = OnlineStatus.ONLINE
        else:
            newstatus = OnlineStatus.OFFLINE

        self.logger.info(f'Going {str(newstatus).lower()} on the "{wikiname}" wiki.')

        if newstatus == OnlineStatus.ONLINE:
            python_command = os.path.join(PATHS['venv'], 'bin', 'python3')
            script_file = os.path.join(PATHS['package'], 'bot', 'ryebotscript.py')
            wikidirectory = os.path.join(PATHS['wikis'], wikiname)
            psutil.Popen([python_command, script_file, '_login'], cwd=wikidirectory)
            self.logger.info('Started new Python process for logging in.')
