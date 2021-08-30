from mwclient.errors import AssertUserFailedError


class InvalidUserFile(KeyError):
    def __init__(self, filename: str = '', missing=False):
        self.filename = filename
        self.missing = missing

    def __str__(self):
        if self.missing:
            details = "The file doesn't exist."
        else:
            details = "The file doesn't contain a valid JSON string."
        return f'User credentials file "{self.filename}" is invalid: {details}'


class PatrolRevisionNotSpecified(KeyError):
    pass


class PatrolRevisionInvalid(KeyError):
    pass


class RetriedLoginAndStillFailed(AssertUserFailedError):
    def __init__(self, action, codes):
        self.action = action
        self.codes = codes

    def __str__(self):
        msg = "Tried to re-login but still failed. Attempted action: {}, codes: {}"
        return msg.format(self.action, ', '.join(self.codes))


class InvalidNamespaceName(KeyError):
    pass
