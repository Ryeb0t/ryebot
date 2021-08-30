"""Utility methods related to process management."""

import psutil


def find_procs_by_cmd(cmd: str):
    """Return a list of processes where any of the `cmdline()` list elements contain `cmd`."""
    ls = []
    for process in psutil.process_iter(['cmdline']):
        for cmd_arguments in process.info['cmdline']:
            if cmd in cmd_arguments:
                ls.append(process)
    return ls
