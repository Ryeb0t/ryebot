from custom_mwclient.models.log_entries.log_entry import LogEntry
from custom_mwclient.wiki_client import WikiClient


class MoveLogEntry(LogEntry):
    def __init__(self, log, site: WikiClient):
        super().__init__(log, site)
        self.title = log['params']['target_title']
        self.page = site.client.pages[self.title]
