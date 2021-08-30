import os

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ryebot.bot import PATHS
from ryebot.bot.daemon_handlers import FileModifiedEventHandler
from ryebot.bot.heartbeat import HEARTBEATFILE
from ryebot.bot.loggers import COMMANDLOGFILE, COMMONLOGFILE, WATCHLOGFILE


class CustomLoggingEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def do_log(self, logstr: str, event: FileSystemEvent):
        what = 'directory' if event.is_directory else 'file'
        logstr = f'[eventid {id(event)}] ' + logstr.format(what=what, src=event.src_path)
        self.logger.info(logstr)

    def on_moved(self, event: FileSystemEvent):
        super().on_moved(event)
        self.do_log("Moved {what}: from {src} to %s" % event.dest_path, event)

    def on_created(self, event: FileSystemEvent):
        super().on_created(event)
        self.do_log("Created {what}: {src}", event)

    def on_deleted(self, event: FileSystemEvent):
        super().on_deleted(event)
        self.do_log("Deleted {what}: {src}", event)

    def on_modified(self, event: FileSystemEvent):
        super().on_modified(event)
        logstr = "Modified {what}: {src} (new size %s)" % os.path.getsize(event.src_path)
        self.do_log(logstr, event)


class CustomEventHandler(CustomLoggingEventHandler):
    def __init__(self, watchdog_logger, common_logger):
        super().__init__(watchdog_logger)
        self.common_logger = common_logger

    def on_modified(self, event: FileSystemEvent):
        if os.path.basename(event.src_path) in (COMMONLOGFILE,
            COMMANDLOGFILE, WATCHLOGFILE, HEARTBEATFILE):
            # do not log modifications of the log files,
            # partly to prevent an infinite logging loop
            return
        if event.src_path == PATHS['localdata']:
            # do not log modifications of the localdata directory, because these are likely
            # caused by the loggers (also the heartbeat in particular) and have little meaning
            return
        super().on_modified(event) # log standard "Modified ..." message
        if not event.is_directory:
            # do whatever action the file modification instructed to do
            FileModifiedEventHandler(self.common_logger, event.src_path).handle()


def start_monitoring(watchdog_logger, common_logger):
    monitored_directory = PATHS['localdata']

    observer = Observer()
    observer.name = "WatchdogThread"
    observer.schedule(CustomEventHandler(watchdog_logger, common_logger),
        monitored_directory, recursive=True)

    watchdog_logger.info(f'Now listening to all changes to the "{monitored_directory}" '
        'directory and its subdirectories, recursively.')
    observer.start()
