import os
from enum import Enum
from pathlib import Path
import time

import click

from ryebot.bot import PATHS
from ryebot.bot.wiki_manager import ONLINESTATUSFILENAME, LOGINSTATUSFILENAME, get_local_wikis


class OnlineStatus(Enum):
    OFFLINE = 0
    ONLINE = 1

    def __str__(self):
        strmap = {
            'OFFLINE': 'Offline',
            'ONLINE': 'Online'
        }
        return strmap[self.name]


class LoginStatus(Enum):
    LOGGED_OUT = 0
    LOGGING_IN = 1
    LOGGED_IN = 2

    def __str__(self):
        strmap = {
            'LOGGED_OUT': 'logged out',
            'LOGGING_IN': 'logging in',
            'LOGGED_IN': 'logged in'
        }
        return strmap[self.name]


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


def _read_onlinestatusfile(wiki, return_default=False):
    if return_default:
        return OnlineStatus.OFFLINE
    
    onlinestatusfile = os.path.join(PATHS['wikis'], wiki, ONLINESTATUSFILENAME)
    if os.path.exists(onlinestatusfile):
        filesize = os.stat(onlinestatusfile).st_size
        if filesize > 0:
            return OnlineStatus.ONLINE
    else:
        Path(onlinestatusfile).touch() # create the file
    return OnlineStatus.OFFLINE


def _read_loginstatusfile(wiki, return_default=False):
    status_dict = {
        'current_status': LoginStatus.LOGGED_OUT,
        'last_login_time': time.gmtime(0), # Jan 1, 1970
        'last_logout_time': time.gmtime(0)
    }
    if return_default:
        return status_dict
    
    loginstatusfile = os.path.join(PATHS['wikis'], wiki, LOGINSTATUSFILENAME)
    if os.path.exists(loginstatusfile):
        with open(loginstatusfile) as f:
            current_status = f.readline().strip()
            last_login_time = f.readline().strip()
            last_logout_time = f.readline().strip()

        try:
            status_dict['current_status'] = LoginStatus(int(current_status))
        except ValueError:
            # either conversion from string to int failed, or the number is not in the enum,
            # so just leave the status at logged out
            pass
        try:
            status_dict['last_login_time'] = time.gmtime(float(last_login_time))
        except ValueError:
            pass
        try:
            status_dict['last_logout_time'] = time.gmtime(float(last_logout_time))
        except ValueError:
            pass

    else:
        Path(loginstatusfile).touch() # create the file

    return status_dict
        

def _get_statuses(wikis, registered_wikis):
    statuses = {}
    for wiki in wikis:
        # check the online and the login status files, and if the
        # wiki is not registered, then just return the default values
        wiki_is_unregistered = wiki not in registered_wikis
        statuses[wiki] = {
            'unregistered': wiki_is_unregistered,
            'onlinestatus': _read_onlinestatusfile(wiki, return_default=wiki_is_unregistered),
            'loginstatus': _read_loginstatusfile(wiki, return_default=wiki_is_unregistered)
        }
    return statuses


def _format_statuses(statuses):
    unregistereds = []
    unregistereds_str = ''
    status_str = ''

    for wiki in sorted(list(statuses.keys())):
        if statuses[wiki]['unregistered']:
            unregistereds.append(wiki)
            continue

        onlinestatus = str(statuses[wiki]['onlinestatus'])
        loginstatus = str(statuses[wiki]['loginstatus']['current_status'])

        time_format = '%a, %d %b %Y %H:%M:%S UTC' # RFC5322 format

        last_login = '?'
        last_login_time = statuses[wiki]['loginstatus']['last_login_time']
        if last_login_time != time.gmtime(0):
            # only use the time from the status if it is not Jan 1, 1970
            last_login = time.strftime(time_format, last_login_time)

        last_logout = '?'
        last_logout_time = statuses[wiki]['loginstatus']['last_logout_time']
        if last_logout_time != time.gmtime(0):
            last_logout = time.strftime(time_format, last_logout_time)

        status_str += f'\n  # {wiki}   {onlinestatus}, {loginstatus}. Last login: {last_login}. Last logout: {last_logout}.'
    
    if len(unregistereds) > 0:
        unregistereds_str = '\n'.join((
            'Could not display the status of the bot in the following wikis:',
            '    '.join(unregistereds),
            'This is because the bot does not have access to those wikis. You can grant access using "ryebot wiki add".'
        ))

    return status_str, unregistereds_str
