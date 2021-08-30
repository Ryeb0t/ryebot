import os
import shutil

from ryebot.bot import PATHS
from ryebot.bot.utils import get_wiki_directory_from_name, get_wiki_directory_from_path


def add_wiki(wikiname):
    """Make a directory for the wiki."""

    wiki_directory = os.path.join(PATHS['wikis'], *get_wiki_directory_from_path(wikiname))
    os.makedirs(wiki_directory)


def remove_wiki(wikiname):
    """Remove the entire directory of the wiki."""

    wiki_directory = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wikiname))
    shutil.rmtree(wiki_directory)
