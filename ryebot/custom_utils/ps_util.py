import psutil


def find_procs_by_cmd(cmd):
    """Return a list of processes where any of the `cmdline()` list elements contain `cmd`."""
    ls = []
    for p in psutil.process_iter(['cmdline']):
        for c in p.info['cmdline']:
            if cmd in c:
                ls.append(p)
    return ls