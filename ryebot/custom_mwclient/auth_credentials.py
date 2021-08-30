import json
import os

from .errors import InvalidUserFile


class AuthCredentials(object):
    username = None
    password = None

    def __init__(self, credentials_file):
        """Store username and password for future use with a WikiClient.

        Username and password are taken from the `credentials_file`,
        which should be a JSON file with a "username" key and a "password" key.
        """
        if not os.path.exists(credentials_file):
            raise InvalidUserFile(credentials_file, missing=True)

        with open(credentials_file) as f:
            json_data = json.load(f)
        if json_data:
            self.password = json_data['password']
            self.username = json_data['username']
        else:
            raise InvalidUserFile(credentials_file)
