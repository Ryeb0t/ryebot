import os
from enum import Enum
from pathlib import Path

import click

from ryebot.bot import PATHS
from .wiki_manager import ONLINESTATUSFILENAME, get_local_wikis


class OnlineStatus(Enum):
    OFFLINE = 0
    ONLINE = 1
    UNREGISTERED = 2
    

def display_status(requested_wikis):
    registered_wikis = get_local_wikis()

    if len(requested_wikis) == 0:
        # no specific wiki requested, so display status for all
        requested_wikis = registered_wikis
    
    statuses = _get_statuses(requested_wikis, registered_wikis)
    status_str, unregistereds_str = _format_statuses(statuses)

    output_str = ''
    if status_str == '' and unregistereds_str == '' and len(requested_wikis) == 0:
        output_str = 'The bot currently has no access to any wikis. Add one using "ryebot wiki add"!'
    
    elif status_str == '' and unregistereds_str != '':
        output_str = unregistereds_str

    elif status_str != '':
        output_str = 'Online status of the bot:{}'.format(status_str)
        if unregistereds_str != '':
            output_str += '\n\n' + unregistereds_str
    
    if output_str == '':
        raise Exception('Error while checking the status of the bot in each wiki!')

    click.echo(output_str)


def _get_statuses(wikis, registered_wikis):
    statuses = {}
    for wiki in wikis:
        # check if the wiki is registered
        if wiki not in registered_wikis:
            statuses[wiki] = OnlineStatus.UNREGISTERED
            continue

        # check the statusfile for the wiki
        statusfile = os.path.join(PATHS['wikis'], wiki, ONLINESTATUSFILENAME)
        if os.path.exists(statusfile):
            filesize = os.stat(statusfile).st_size
            if filesize > 0:
                statuses[wiki] = OnlineStatus.ONLINE
            else:
                statuses[wiki] = OnlineStatus.OFFLINE
        else:
            Path(statusfile).touch() # create the file
            statuses[wiki] = OnlineStatus.OFFLINE
    
    return statuses


def _format_statuses(statuses):
    unregistereds = []
    unregistereds_str = ''
    status_str = ''

    for wiki in sorted(list(statuses.keys())):
        if statuses[wiki] == OnlineStatus.UNREGISTERED:
            unregistereds.append(wiki)
            continue
        wikistatus = 'Online' if statuses[wiki] == OnlineStatus.ONLINE else 'Offline'
        status_str += f'\n  # {wiki}   {wikistatus}'
    
    if len(unregistereds) > 0:
        unregistereds_str = '\n'.join((
            'Could not display the status of the bot in the following wikis:',
            '    '.join(unregistereds),
            'This is because the bot does not have access to those wikis. You can grant access using "ryebot wiki add".'
        ))

    return status_str, unregistereds_str
