import json
import os

from .errors import InvalidUserFile
from ryebot.bot import PATHS


class AuthCredentials(object):
    file_pattern = 'wiki_account_{}.json'
    username = None
    password = None

    def __init__(self, user_name):
        """
        Stores username and password for future use with a WikiClient.
        Username and password are taken from a JSON file in the global config
        directory that should have a "username" key and a "password" key.
        :param user_name: Name of the user for which a JSON file with credentials exists
        """

        if not user_name:
            return

        credentials_file = os.path.join(PATHS['global_config'], self.file_pattern.format(user_name.lower()))
        if not os.path.exists(credentials_file):
            raise InvalidUserFile
        
        with open(credentials_file) as f:
            json_data = json.load(f)
        if json_data:
            self.password = json_data['password']
            self.username = json_data['username']
        else:
            raise InvalidUserFile
        