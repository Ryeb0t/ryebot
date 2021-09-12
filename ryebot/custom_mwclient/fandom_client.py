from typing import Union, List

from mwclient import InvalidResponse

from .auth_credentials import AuthCredentials
from .site import Site
from .wiki_client import WikiClient
from custom_utils.string_util import str_to_list


class FandomClient(WikiClient):
    """
    Functions for connecting to and editing specifically Fandom wikis.
    """
    client: Site = None
    wiki: str = None

    def __init__(self, wiki: str, client: Site = None, lang: str = None,
                 credentials: AuthCredentials = None, **kwargs):
        """
        Create a site object.
        :param wiki: Name of a wiki
        :param lang: Optional. If the wiki has a language path in the URL, provide it here.
        :param client: Optional. If this is provided, SessionManager will not be used.
        :param credentials: Optional. Provide if you want a logged-in session.
        """

        url = '{}.fandom.com'.format(wiki)
        self.lang = '/' + ('' if lang is None else lang + '/')
        super().__init__(
            url=url, path=self.lang, credentials=credentials,
            client=client, **kwargs
        )

    def relog(self):
        super().relog()

    def login(self):
        if self.credentials is None:
            return
        try:
            self.client.login(
                username=self.credentials.username,
                password=self.credentials.password
            )
        except InvalidResponse:
            self.url = self.url.replace('gamepedia', 'fandom')
            self.relog()

    def search(self, search_term: str, title_list: List[str], limit: int = 500):
        """
        Searches a specified list of titles for a given term.
        A replacement for Fandom's lack of insource search.

        This method paginates the requests to fetch page sources, so it's relatively efficient,
        especially if you are logged in as an administrator with apihighlimits.

        :param search_term: The term to search
        :param title_list: A list of page titles.
        :param limit: The pagination limit when querying for page texts.
        If you are logged out or not a systop, probably 50.
        :return:
        """

        # TODO: Add regex support

        page_list = self.get_simple_pages(title_list, limit=limit)
        for page in page_list:
            if search_term in page.text:
                print(page.name)

    def search_namespace(self, search_term: str, namespace: Union[int, str], limit: int = 500):
        """
        Searches a specified namespace for a search term.

        If you want to search the entire wiki, use search instead.
        :param search_term: The term to search
        :param namespace: The namespace within which to search for the term.
        :param limit: The pagination limit when querying for page texts.
        If you are logged out or not a systop, probably 50.
        :return:
        """
        if isinstance(namespace, str):
            namespace = self.get_ns_number(namespace)
        self.search(
            search_term,
            self.client.allpages(namespace=namespace, generator=False),
            limit=limit
        )


    ##### Wiki-specific functions


    # terraria
    def get_wikis_from_str(self, wikis_str: str, log, delimiter: str = ','):
        """Returns a list of wikis that is normalized and only includes valid (off-wiki) wikis.

        Parameters
        ----------
        1. wiki_str : str
            - List of wikis as a string.
        2. delimiter: str
            - Delimiter between the wikis in `wiki_str`.
        """

        try:
            # dynamic list
            valid_wikis = str_to_list(self.client.expandtemplates(text='{{langList|offWiki}}'))
        except Exception:
            log('\n***ERROR*** while expanding "{{langList|offWiki}}"!')
            log(exc_info=True, s='Error message:\n')
            # fallback: hardcoded list
            valid_wikis = ["de", "fr", "hu", "ko", "ru", "pl", "pt", "uk", "zh"]
            log('Setting valid_wikis to hard-coded list: ' + str(valid_wikis))

        wikis_raw = str_to_list(wikis_str, delim=delimiter)
        wikis = []
        for wiki in wikis_raw:
            if wiki in valid_wikis:
                wikis.append(wiki)
            else:
                log('Warning: Wiki "{}" from config isn\'t valid! Dismissing it.'.format(wiki))

        return wikis
