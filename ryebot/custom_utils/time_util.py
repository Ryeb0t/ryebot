"""Utility methods related to operations including times and durations."""

import datetime
import time


def start_timecount() -> float:
    """Return the current time."""
    return time.time()


def end_timecount(start_time: int) -> str:
    """Return a string of the time passed since the `start_time`."""
    micros_start = start_time * 1000000
    micros_end = time.time() * 1000000
    delta = datetime.timedelta(microseconds=micros_end - micros_start)
    return 'Duration: {}'.format(delta)


def stdtimeformat_file(use_localtime: bool = True):
    """Convert the current time to a standard time format to be used in file names.

    Parameters
    ----------
    1. use_localtime : bool
        - Whether to use local time instead of UTC.
    """

    if use_localtime:
        t_struct = time.localtime()
    else:
        t_struct = time.gmtime()

    return time.strftime(stdtimeformat_file_str(), t_struct)

def stdtimeformat_file_from_secs(secs: int):
    """Convert the specified `secs` to a standard time format to be used in file names."""
    return time.strftime(stdtimeformat_file_str(), time.gmtime(secs))

def stdtimeformat_file_str():
    """Return a standard time format string.

    The format is as follows:

    `year-month-day_hour-minute-second`
    """

    return "%Y-%m-%d_%H-%M-%S"


def format_secs(secs, format="%a, %d %b %Y %H:%M:%S"):
    """Format a number of seconds in a specified date/time format.

    Also append ` (UTC)`.

    Parameters
    ----------
    1. secs : int | time.struct_time
        - The number of seconds or time struct to format.
    2. format : str
        - The format.
        The default format is as follows:

        `weekday, day monthabbr year hours:minutes:seconds`

    For the formatting syntax, see
    https://docs.python.org/3/library/time.html#time.strftime.
    """

    if isinstance(secs, time.struct_time):
        # parameter is already a struct
        time_struct = secs
    else:
        time_struct = time.gmtime(secs)
    timestr = time.strftime(format, time_struct)
    return timestr + ' (UTC)'


def asctime_std():
    """Convert the current UTC time to a standard format.

    The format is as follows:

    `weekday month day hour:minute:second year`

    Example: `Sat Jun  6 16:26:11 1998`
    """

    return time.asctime(time.gmtime())
