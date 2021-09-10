from custom_mwclient.wiki_client import WikiClient


class SimplePage():
    """A data container holding the name of a page and its text. Not capable of any operations."""

    def __init__(self, name: str, text: str, exists: bool):
        self.name = name
        self.text = text
        self.exists = exists


class Namespace():
    """A data container holding information about a namespace.

    It holds the id, name, canonical name, and aliases of a namespace. It is not
    capable of any operations.
    """

    def __init__(self, id_number: int = None, name: str = None,
                 canonical_name: str = None, aliases: list = None):
        self.id = id_number
        self.name = name
        self.canonical_name = canonical_name
        self.aliases = aliases or []


class LogEntry():
    """A data container holding information about a log entry.

    It holds information like entry type, page name, or log ID. It is not
    capable of any operations.
    """

    def __init__(self, log, site: WikiClient):
        self.site = site
        self.log_type = log['type']
        self.title = log['title']
        self.page = site.client.pages[self.title]
        self.logid = log['logid']
        self.comment = log['comment']
        self.user = log['user']


class MoveLogEntry(LogEntry):
    """A data container holding information about a move log entry."""

    def __init__(self, log, site: WikiClient):
        super().__init__(log, site)
        self.title = log['params']['target_title']
        self.page = site.client.pages[self.title]
