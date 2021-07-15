import logging
import os

from ryebot.bot import PATHS
from ryebot.bot.wiki_manager import STATUSFILENAME


class FileModifiedEventHandler():

    def __init__(self, logger: logging.Logger, file_path: str):
        self.logger = logger
        self.file_path = file_path

    def handle(self):
        logstr = f"File {self.file_path} was modified. New size: {os.path.getsize(self.file_path)}."
        self.logger.info(logstr, extra={'pid': os.getpid()})

        # a file was modified, so the daemon is supposed to do something.
        # we use the following methods to find out what that is, based on the file path, content, size, etc.

        # changes to the online status on a wiki
        self.onlinestatus()


    def onlinestatus(self):
        if os.path.basename(self.file_path) != STATUSFILENAME:
            return
        if os.path.dirname(os.path.dirname(self.file_path)) != PATHS['wikis']:
            return
        wikiname = os.path.basename(os.path.dirname(self.file_path))
        newstatus = 'online' if os.stat(self.file_path).st_size > 0 else 'offline'
        self.logger.info(f'Going {newstatus} on the "{wikiname}" wiki.', extra={'pid': os.getpid()})
