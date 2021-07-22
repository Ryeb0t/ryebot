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


class StatusDisplayer():

    def __init__(self, requested_wikis):
        self.statuses = {}
        self.status_str = ''
        self.unregistereds_str = ''
        self.output_str = ''

        self.registered_wikis = get_local_wikis()
        self.unregistered_wikis = []
        self.requested_wikis = []

        if len(requested_wikis) == 0:
            # no specific wiki requested, so display status for all
            self.requested_wikis = self.registered_wikis
        else:
            for wiki in requested_wikis:
                if wiki in self.registered_wikis:
                    self.requested_wikis.append(wiki)
                else:
                    self.unregistered_wikis.append(wiki)


    def display(self):

        if len(self.requested_wikis) == 0 and len(self.unregistered_wikis) == 0:
            click.echo('The bot currently has no access to any wikis. Add one using "ryebot wiki add"!')
            return

        self._get_statuses()
        self._format_statuses()
        self._make_output_string()

        if self.output_str == '':
            raise Exception('Error while checking the status of the bot in each wiki!')

        click.echo(self.output_str)


    def _get_statuses(self):
        for wiki in self.requested_wikis:
            self.statuses[wiki] = {
                'onlinestatus': self._read_onlinestatusfile(wiki),
                'loginstatus': self._read_loginstatusfile(wiki)
            }


    def _format_statuses(self):
        for wiki in sorted(list(self.statuses.keys())):
            onlinestatus = str(self.statuses[wiki]['onlinestatus'])
            loginstatus = str(self.statuses[wiki]['loginstatus']['current_status'])

            time_format = '%a, %d %b %Y %H:%M:%S UTC' # RFC5322 format

            last_login = '?'
            last_login_time = self.statuses[wiki]['loginstatus']['last_login_time']
            if last_login_time != time.gmtime(0):
                # only use the time from the status if it is not Jan 1, 1970
                last_login = time.strftime(time_format, last_login_time)

            last_logout = '?'
            last_logout_time = self.statuses[wiki]['loginstatus']['last_logout_time']
            if last_logout_time != time.gmtime(0):
                last_logout = time.strftime(time_format, last_logout_time)

            self.status_str += f'\n  # {wiki}   {onlinestatus}, {loginstatus}. Last login: {last_login}. Last logout: {last_logout}.'

        if len(self.unregistered_wikis) > 0:
            self.unregistereds_str = '\n'.join((
                'Could not display the status of the bot in the following wikis:',
                '    '.join(self.unregistered_wikis),
                'This is because the bot does not have access to those wikis. You can grant access using "ryebot wiki add".'
            ))


    def _make_output_string(self):
        self.output_str = ''
        if self.status_str == '' and self.unregistereds_str != '':
            self.output_str = self.unregistereds_str

        elif self.status_str != '':
            self.output_str = 'Current status of the bot:{}'.format(self.status_str)
            if self.unregistereds_str != '':
                self.output_str += '\n\n' + self.unregistereds_str


    def _read_onlinestatusfile(self, wiki: str):
        if wiki in self.unregistered_wikis:
            return OnlineStatus.OFFLINE

        onlinestatusfile = os.path.join(PATHS['wikis'], wiki, ONLINESTATUSFILENAME)
        if os.path.exists(onlinestatusfile):
            filesize = os.stat(onlinestatusfile).st_size
            if filesize > 0:
                return OnlineStatus.ONLINE
        else:
            Path(onlinestatusfile).touch() # create the file
        return OnlineStatus.OFFLINE


    def _read_loginstatusfile(self, wiki: str):
        status_dict = {
            'current_status': LoginStatus.LOGGED_OUT,
            'last_login_time': time.gmtime(0), # Jan 1, 1970
            'last_logout_time': time.gmtime(0)
        }
        if wiki in self.unregistered_wikis:
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
