import time

import click
from beautifultable import BeautifulTable

from ryebot.bot.utils import get_local_wikis
from ryebot.bot.mgmt.logincontrol import ELoginControlCommand, LoginControl
from ryebot.bot.mgmt.loginstatus import ELoginStatus, LoginStatus


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
                'logincontrol': self._read_logincontrolfile(wiki),
                'loginstatus': self._read_loginstatusfile(wiki)
            }


    def _format_statuses(self):
        statustable = BeautifulTable()

        for wiki in sorted(list(self.statuses.keys())):
            logincontrol = str(self.statuses[wiki]['logincontrol'])
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

            statustable.rows.append([wiki, loginstatus, logincontrol, last_login])

        if len(statustable.rows) > 0:
            statustable.columns.header = ["WIKI", "STATUS", "CTRLCMD", "LASTLOGIN"]
            statustable.columns.alignment = BeautifulTable.ALIGN_LEFT
            statustable.columns.padding_right["WIKI"] = 3
            statustable.set_style(BeautifulTable.STYLE_NONE)
            self.status_str = str(statustable)


    def _make_output_string(self):
        if len(self.unregistered_wikis) > 0:
            self.unregistereds_str = '\n'.join((
                'Could not display the status of the bot in the following wikis:',
                '    '.join(self.unregistered_wikis),
                'This is because the bot does not have access to those wikis. You can grant access using "ryebot wiki add".'
            ))

        if self.status_str == '' and self.unregistereds_str != '':
            self.output_str = self.unregistereds_str

        elif self.status_str != '':
            self.output_str = 'Current status of the bot:\n' + self.status_str
            if self.unregistereds_str != '':
                self.output_str += '\n\n' + self.unregistereds_str


    def _read_logincontrolfile(self, wiki: str):
        if wiki in self.unregistered_wikis:
            return ELoginControlCommand.DO_NOTHING
        return LoginControl(wiki=wiki).command


    def _read_loginstatusfile(self, wiki: str):
        if wiki in self.unregistered_wikis:
            return {
                'current_status': ELoginStatus.LOGGED_OUT,
                'last_login_time': time.gmtime(0), # Jan 1, 1970
                'last_logout_time': time.gmtime(0)
            }

        all_info = LoginStatus(wiki=wiki).all_info
        return {
            'current_status': all_info[0],
            'last_login_time': all_info[1],
            'last_logout_time': all_info[2]
        }
