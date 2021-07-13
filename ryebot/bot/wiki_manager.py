import os
import shutil
from pathlib import Path

import click

from ryebot.bot import PATHS


# Name of the file that holds the online status for the wiki.
# This file is either empty (which means the bot is offline on
# the wiki) or contains a single byte (which means it is online).
# If it doesn't exist, then it must have been removed at some point
# and will be recreated.
STATUSFILENAME = '.onlinestatus'


def get_local_wikis():
    """Return a list of the wikis that are registered in the `localdata/wikis` directory, i.e., that the bot has access to."""
    return os.listdir(PATHS['wikis'])


def display_wiki_list():
    wikis = get_local_wikis()

    output_str = ''
    if len(wikis) > 0:
        output_str = f'The bot currently has access to the following {len(wikis)} wiki(s):\n'
        output_str += '    '.join(wikis)
        output_str += '\nUse "ryebot status" to review the bot\'s status in each wiki, and "ryebot wiki remove" to withdraw access from a wiki.'
    else:
        output_str = 'The bot currently does not have access to any wiki.\nYou can grant access using "ryebot wiki add".'

    click.echo(output_str)


def add_wiki(wikiname):
    wikis = get_local_wikis()

    if wikiname in wikis:
        click.echo(f'The bot already has access to the "{wikiname}" wiki!')
        return
    
    # make new directory and standard files
    new_wiki_directory = os.path.join(wikis, wikiname)
    os.mkdir(new_wiki_directory)
    Path(os.path.join(new_wiki_directory, STATUSFILENAME)).touch() # create the onlinestatus file
    click.echo(f'Granted the bot access to the "{wikiname}" wiki!')


def remove_wiki(wikiname):
    wikis = get_local_wikis()

    if wikiname not in wikis:
        click.echo(f'Cannot withdraw access from the "{wikiname}" wiki, because the bot currently does not have access to it.')
        return
    
    # remove entire contents of the wiki directory
    shutil.rmtree(os.path.join(wikis, wikiname))
    click.echo(f'The bot now has no access to the "{wikiname}" wiki any longer!')
    