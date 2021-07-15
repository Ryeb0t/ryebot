import logging
import os
import time

from daemon import DaemonContext
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from ryebot.bot import PATHS
from ryebot.bot.wiki_manager import STATUSFILENAME


LOGFILE = '.log'


class CustomLoggingEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, logger=None):
        super().__init__()

        self.logger = logger or logging.root

    def do_log(self, logstr: str, event: FileSystemEvent):
        logstr = logstr.format(
            what='directory' if event.is_directory else 'file',
            src=event.src_path,
            # only move-events have the dest_path attribute
            dst=event.dest_path if hasattr(event, 'dest_path') else ''
        )
        self.logger.info(logstr, extra={'pid': os.getpid()})

    def on_moved(self, event):
        super().on_moved(event)

        self.do_log("(watchdog) Moved {what}: from {src} to {dst}", event)

    def on_created(self, event):
        super().on_created(event)

        self.do_log("(watchdog) Created {what}: {src}", event)

    def on_deleted(self, event):
        super().on_deleted(event)

        self.do_log("(watchdog) Deleted {what}: {src}", event)

    def on_modified(self, event):
        super().on_modified(event)

        self.do_log("(watchdog) Modified {what}: {src}", event)


class CustomEventHandler(CustomLoggingEventHandler):
    def __init__(self, logger=None):
        super().__init__(logger)

    def _handle_onlinestatus_event(self, file_path):
        if os.path.basename(file_path) != STATUSFILENAME:
            return
        if os.path.dirname(os.path.dirname(file_path)) != PATHS['wikis']:
            return
        wikiname = os.path.basename(os.path.dirname(file_path))
        newstatus = 'online' if os.stat(file_path).st_size > 0 else 'offline'
        self.logger.info(f'Going {newstatus} on the "{wikiname}" wiki.', extra={'pid': os.getpid()})

    def _handle_file_event(self, file_path):
        logstr = f"File {file_path} was modified. New size: {os.path.getsize(file_path)}."
        self.logger.info(logstr, extra={'pid': os.getpid()})
        self._handle_onlinestatus_event(file_path)

    def on_modified(self, event):
        if os.path.basename(event.src_path) == LOGFILE:
            # do not log modifications of the log file, because those are caused by ourselves
            # and we don't want an infinite logging loop
            return

        super().on_modified(event)

        if not event.is_directory:
            self._handle_file_event(event.src_path)

    def on_created(self, event):
        super().on_created(event)

        if not event.is_directory:
            self._handle_file_event(event.src_path)

def start_monitoring():
    monitored_directory = PATHS['localdata']
    observer = Observer()
    observer.schedule(CustomEventHandler(), monitored_directory, recursive=True)
    logging.info(f'Now listening to all changes to the "{monitored_directory}" directory and its subdirectories, recursively.')
    observer.start()


def main():
    logging.basicConfig(level=logging.INFO, filename=os.path.join(PATHS['localdata'], LOGFILE),
        format='[%(asctime)s] [pid %(pid)d] %(message)s', datefmt='%a %b %d %H:%M:%S %Y')

    start_monitoring()

    while True:
        time.sleep(6)
        logging.info('heartbeat from daemon', extra={'pid': os.getpid()})


if __name__ == '__main__':
    with DaemonContext():
        main()