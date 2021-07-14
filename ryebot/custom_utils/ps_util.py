import psutil


def find_procs_by_name(name):
    """Return a list of processes whose `cmdline()` list contains `name`."""
    ls = []
    for p in psutil.process_iter(['cmdline']):
        if name in p.info['cmdline']:
            ls.append(p)
    return ls