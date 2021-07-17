import logging
import os
import time

from daemon import DaemonContext
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from ryebot.bot import PATHS
from ryebot.bot.daemon_handlers import FileModifiedEventHandler
from ryebot.bot.loggers import common_logger, watchdog_logger, WATCHLOGFILE


# File that will be edited by the daemon in a set interval, to signify that it is alive
HEARTBEATFILE = '.heartbeat'


class CustomLoggingEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger or logging.root

    def do_log(self, logstr: str, event: FileSystemEvent):
        what='directory' if event.is_directory else 'file',
        logstr = logstr.format(what=what, src=event.src_path)
        self.logger.info(logstr)

    def on_moved(self, event):
        super().on_moved(event)
        logstr = "(watchdog) Moved {{what}}: from {{src}} to {dst} (new size {size})"
        logstr = logstr.format(dst=event.dest_path, size=os.path.getsize(event.dest_path))  
        self.do_log(logstr, event)

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

    def on_modified(self, event):
        if os.path.basename(event.src_path) in (WATCHLOGFILE, HEARTBEATFILE):
            # do not log modifications of the log file, because those are caused by ourselves
            # and we don't want an infinite logging loop
            return
        super().on_modified(event) # log standard "Modified ..." message
        if not event.is_directory:
            # do whatever action the file modification instructed to do
            FileModifiedEventHandler(common_logger(), event.src_path).handle()

    def on_created(self, event):
        super().on_created(event) # log standard "Created ..." message
        if not event.is_directory:
            FileModifiedEventHandler(common_logger(), event.src_path).handle()


def start_monitoring(logger: logging.Logger=None):
    monitored_directory = PATHS['localdata']
    observer = Observer()
    observer.name = "tWatchdog"
    observer.schedule(CustomEventHandler(logger), monitored_directory, recursive=True)
    logger.info(f'Now listening to all changes to the "{monitored_directory}" directory and its subdirectories, recursively.')
    observer.start()


def do_heartbeat():
    time.sleep(6)
    with open(os.path.join(PATHS['localdata'], HEARTBEATFILE), 'w') as f:
        f.write(time.strftime('%a, %d %b %Y %H:%M:%S UTC')) # RFC5322 format


def main():
    start_monitoring(watchdog_logger())
    while True:
        do_heartbeat()


if __name__ == '__main__':
    with DaemonContext():
        main()