import logging
import os
import time

from daemon import DaemonContext
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from ryebot.bot import PATHS
from ryebot.bot.daemon_handlers import FileModifiedEventHandler


# Name of the file that contains everything logged by the daemon
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
        self.logger.info(logstr)

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

    def on_modified(self, event):
        if os.path.basename(event.src_path) == LOGFILE:
            # do not log modifications of the log file, because those are caused by ourselves
            # and we don't want an infinite logging loop
            return
        super().on_modified(event) # log standard "Modified ..." message
        if not event.is_directory:
            # do whatever action the file modification instructed to do
            FileModifiedEventHandler(self.logger, event.src_path).handle()

    def on_created(self, event):
        super().on_created(event) # log standard "Created ..." message
        if not event.is_directory:
            FileModifiedEventHandler(self.logger, event.src_path).handle()


def start_monitoring():
    monitored_directory = PATHS['localdata']
    observer = Observer()
    observer.schedule(CustomEventHandler(), monitored_directory, recursive=True)
    logging.info(f'Now listening to all changes to the "{monitored_directory}" directory and its subdirectories, recursively.')
    observer.start()


def do_heartbeat():
    time.sleep(6)
    with open(os.path.join(PATHS['localdata'], '.heartbeat'), 'w') as f:
        f.write(time.strftime('%a, %d %b %Y %H:%M:%S UTC')) # RFC5322 format


def main():
    logging.basicConfig(level=logging.INFO, filename=os.path.join(PATHS['localdata'], LOGFILE),
        format='[%(asctime)s] [pid %(process)d tid %(thread)d] %(message)s', datefmt='%a %b %d %H:%M:%S %Y')

    start_monitoring()
    while True:
        do_heartbeat()


if __name__ == '__main__':
    with DaemonContext():
        main()