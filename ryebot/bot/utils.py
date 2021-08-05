import os

from ryebot.bot import PATHS
from ryebot.bot.cli.wiki_manager import LOGINSTATUSFILE, get_wiki_directory_from_name


def get_login_time(wikiname: str):
    last_login_time = 0.0

    loginstatusfile = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wikiname), LOGINSTATUSFILE)
    if os.path.exists(loginstatusfile):
        with open(loginstatusfile) as f:
            try:
                line = f.readlines()[1] # second line in the file
                last_login_time = float(line.strip())
            except (IndexError, ValueError):
                # reading the second line might have failed,
                # or conversion to float might have failed,
                # so return 0
                pass

    return last_login_time
