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
ONLINESTATUSFILENAME = '.onlinestatus'


def get_local_wikis():
    """Return a list of the wikis that are registered in the `localdata/wikis` directory, i.e., that the bot has access to."""
    return os.listdir(PATHS['wikis'])


def display_wiki_list(only_show_count):
    wikis = get_local_wikis()

    if only_show_count:
        click.echo(len(wikis))
        return

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
    new_wiki_directory = os.path.join(PATHS['wikis'], wikiname)
    os.mkdir(new_wiki_directory)
    Path(os.path.join(new_wiki_directory, ONLINESTATUSFILENAME)).touch() # create the onlinestatus file
    click.echo(f'Granted the bot access to the "{wikiname}" wiki!')


def remove_wiki(wikiname):
    wikis = get_local_wikis()

    if wikiname not in wikis:
        click.echo(f'Cannot withdraw access from the "{wikiname}" wiki, because the bot currently does not have access to it.')
        return
    
    # remove entire contents of the wiki directory
    shutil.rmtree(os.path.join(PATHS['wikis'], wikiname))
    click.echo(f'The bot now does not have access to the "{wikiname}" wiki any longer!')


def go_online_on_wiki(wikinames, on_all_wikis):
    wikis = get_local_wikis()

    if on_all_wikis:
        # if we should go online on all wikis, then don't disregard the "wikinames" input
        # so that invalid wikinames there can still be pointed out
        wikinames = set(list(wikinames) + wikis) # set removes duplicate values

    for wikiname in sorted(wikinames):
        
        if wikiname not in wikis:
            click.echo('\n'.join((
                f'Cannot go online on the "{wikiname}" wiki, because the bot currently does not have access to it.',
                'You can grant access to the wiki using "ryebot wiki add".'
            )))
            continue

        statusfile = os.path.join(PATHS['wikis'], wikiname, ONLINESTATUSFILENAME)

        if not os.path.exists(statusfile):
            Path(statusfile).touch() # create the file

        output_str = f'Going online on the "{wikiname}" wiki.'
        if os.stat(statusfile).st_size > 0 and not on_all_wikis:
            # do not display this message if we should go online on all wikis
            if on_all_wikis:
                output_str = ''
            else:
                output_str = f'Already online on the "{wikiname}" wiki.'

        with open(statusfile, 'w') as f:
            # always set the file's content to "1", even if it already is "1" or even something else for some reason
            f.write('1')

        if output_str != '':
            click.echo(output_str)


def go_offline_on_wiki(wikinames, on_all_wikis):
    wikis = get_local_wikis()

    if on_all_wikis:
        # if we should go offline on all wikis, then don't disregard the "wikinames" input
        # so that invalid wikinames there can still be pointed out
        wikinames = set(list(wikinames) + wikis) # set removes duplicate values

    for wikiname in sorted(wikinames):

        if wikiname not in wikis:
            click.echo('\n'.join((
                f'Cannot go offline on the "{wikiname}" wiki, because the bot currently does not have access to it.',
                'You can grant access to the wiki using "ryebot wiki add".'
            )))
            return

        statusfile = os.path.join(PATHS['wikis'], wikiname, ONLINESTATUSFILENAME)

        if not os.path.exists(statusfile):
            Path(statusfile).touch() # create the file

        output_str = f'Going offline on the "{wikiname}" wiki.'
        if os.stat(statusfile).st_size == 0:
            # do not display this message if we should go offline on all wikis
            if on_all_wikis:
                output_str = ''
            else:
                output_str = f'Already offline on the "{wikiname}" wiki.'

        with open(statusfile, 'w') as f:
            # always set the file's content to nothing
            f.write('')

        if output_str != '':
            click.echo(output_str)
