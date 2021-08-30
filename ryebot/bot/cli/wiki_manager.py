import os
import shutil
from pathlib import Path

import click

from ryebot.bot import PATHS
from ryebot.bot.logincontrol import ELoginControlCommand, LoginControl


# Name of the file that contains the command for the daemon.
# This file is empty if there is currently no command to login
# or logout. It contains a single byte if the daemon should login
# and two bytes if the daemon should logout.
LOGINCONTROLFILE = '.login.control'

# Name of the file that holds the login status for the wiki.
# This file contains three lines: 1) the status (0 - logged out,
# 1 - logging in, 2 - logged in), 2) the time of the last successful
# login, and 3) the time of the last logout. Both times are in
# seconds since the Unix epoch.
LOGINSTATUSFILE = '.login.status'


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
    new_wiki_directory = os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wikiname))
    os.makedirs(new_wiki_directory)
    Path(os.path.join(new_wiki_directory, LOGINCONTROLFILE)).touch() # create the login control command file
    Path(os.path.join(new_wiki_directory, LOGINSTATUSFILE)).touch() # create the login status file
    click.echo(f'Granted the bot access to the "{wikiname}" wiki!')


def remove_wiki(wikiname):
    wikis = get_local_wikis()

    if wikiname not in wikis:
        click.echo(f'Cannot withdraw access from the "{wikiname}" wiki, because the bot currently does not have access to it.')
        return

    # remove entire contents of the wiki subdirectory
    shutil.rmtree(os.path.join(PATHS['wikis'], *get_wiki_directory_from_name(wikiname)))
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

        current_command = LoginControl(wiki=wikiname).command
        if current_command == ELoginControlCommand.DO_LOGIN:
            click.echo(f'Currently already going online on the "{wikiname}" wiki.')
        elif current_command == ELoginControlCommand.DO_LOGOUT:
            click.echo(f'Cannot go online on the "{wikiname}" wiki! Currently going offline there.')
        else:
            click.echo(f'Going online on the "{wikiname}" wiki.')
            LoginControl(wiki=wikiname).command = ELoginControlCommand.DO_LOGIN


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

        current_command = LoginControl(wiki=wikiname).command
        if current_command == ELoginControlCommand.DO_LOGOUT:
            click.echo(f'Currently already going offline on the "{wikiname}" wiki.')
        elif current_command == ELoginControlCommand.DO_LOGIN:
            click.echo(f'Cannot go offline on the "{wikiname}" wiki! Currently going online there.')
        else:
            click.echo(f'Going offline on the "{wikiname}" wiki.')
            LoginControl(wiki=wikiname).command = ELoginControlCommand.DO_LOGOUT
