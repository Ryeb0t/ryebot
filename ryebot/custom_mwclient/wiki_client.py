import datetime
import time
import logging

from mwclient.page import Page
from mwclient.errors import AssertUserFailedError
from mwclient.errors import APIError
from mwclient.errors import ProtectedPageError
from requests.exceptions import ReadTimeout
from typing import Optional, Union, List, Dict
import mwparserfromhell

from custom_mwclient.models.simple_page import SimplePage
from custom_mwclient.models.namespace import Namespace

from .auth_credentials import AuthCredentials
from .errors import RetriedLoginAndStillFailed, InvalidNamespaceName, PatrolRevisionNotSpecified, PatrolRevisionInvalid
from .session_manager import session_manager
from .site import Site


class WikiClient(object):
    """
    Various utilities that extend mwclient and could be useful on any wiki/wiki farm.
    Utilities here should not depend on any extensions.
    There's no intention to develop anything that's not useful on Gamepedia/Gamepedia esports wikis
    but anything that's platform or extension-specific will go in GamepediaSite instead.
    """
    url = None
    client = None
    write_errors = (AssertUserFailedError, ReadTimeout, APIError)

    def __init__(self, url: str, path='/', credentials: AuthCredentials = None, client: Site = None, max_retries=3, retry_interval=10, **kwargs):
        self.scheme = None
        if 'http://' in url:
            self.scheme = 'http'
            url = url.replace('http://', '')
        elif 'https://' in url:
            self.scheme = 'https'
            url = url.replace('https://', '')
        # If user specifies scheme, we'll assume they want that with precedence
        # even over specifying something in the url. Scheme is unlikely enough to be specified
        # that it's not worth making an explicit parameter, especially since we support specifying
        # it via the url.
        if 'scheme' in kwargs:
            self.scheme = kwargs.pop('scheme')

        self.url = url
        self.errors = []
        self.credentials = credentials
        self.path = path
        self.kwargs = kwargs
        self.max_retries = max_retries
        self.retry_interval = retry_interval

        self._namespaces = None
        self._ns_name_to_ns = None

        if client:
            self.client = client
            return

        self.client = session_manager.get_client(url=url, path=path, scheme=self.scheme, credentials=credentials, **kwargs)


    def login(self):
        """Login to the wiki."""
        if self.credentials is None:
            return
        self.client.login(username=self.credentials.username, password=self.credentials.password)


    def relog(self):
        """Completely discards pre-existing session and creates a new site object."""
        # The session manager will log in for us too
        self.client = session_manager.get_client(url=self.url, path=self.path, credentials=self.credentials, **self.kwargs, force_new=True)

    @property
    def namespaces(self):
        if self._namespaces is not None:
            return self._namespaces
        self._populate_namespaces()
        return self._namespaces

    @property
    def ns_name_to_namespace(self) -> Dict[str, Namespace]:
        if self._ns_name_to_ns is not None:
            return self._ns_name_to_ns
        self._populate_namespaces()
        self._ns_name_to_ns: Dict[str, Namespace]
        return self._ns_name_to_ns

    def _populate_namespaces(self):
        result = self.client.api('query', meta='siteinfo', siprop="namespaces|namespacealiases")
        ns_aliases = {}
        for alias in result['query']['namespacealiases']:
            alias_key = str(alias['id'])
            if alias_key not in ns_aliases:
                ns_aliases[alias_key] = []
            ns_aliases[alias_key].append(alias['*'])
        ns_list = []
        ns_map = {}
        for ns_str, ns_data in result['query']['namespaces'].items():
            ns = int(ns_str)
            canonical = ns_data.get('canonical')
            aliases = ns_aliases.get(ns_str)
            ns_obj = Namespace(id_number=ns, name=ns_data['*'],
                               canonical_name=canonical, aliases=aliases)
            ns_list.append(ns_obj)
            ns_map[ns_data['*']] = ns_obj
            if canonical is not None:
                ns_map[canonical] = ns_obj
            if aliases is not None:
                for alias in aliases:
                    ns_map[alias] = ns_obj
        self._namespaces = ns_list
        self._ns_name_to_ns = ns_map

    def get_ns_number(self, ns: str):
        ns_obj = self.ns_name_to_namespace.get(ns)
        if ns_obj is None:
            raise InvalidNamespaceName
        return ns_obj.id

    def pages_using(self, template, namespace: Optional[Union[int, str]] = None, filterredir='all', limit=None, generator=True):
        """Return a list of ``mwclient.page`` objects that are transcluding the specified page."""

        if isinstance(namespace, str):
            namespace = self.get_ns_number(namespace)
        if ':' not in template:
            title = 'Template:' + template
        elif template.startswith(':'):
            title = template[1:]
        else:
            title = template
        return self.client.pages[title].embeddedin(namespace=namespace, filterredir=filterredir, limit=limit, generator=generator)

    def recentchanges_by_interval(self, minutes, offset=0, prop='title|ids|tags|user|patrolled', **kwargs):
        now = datetime.datetime.utcnow() - datetime.timedelta(minutes=offset)
        then = now - datetime.timedelta(minutes=minutes)
        result = self.client.recentchanges(
            start=now.isoformat(),
            end=then.isoformat(),
            limit='max',
            prop=prop,
            **kwargs
        )
        return result

    def recent_titles_by_interval(self, *args, **kwargs):
        revisions = self.recentchanges_by_interval(*args, **kwargs, toponly=0)
        titles = [rev['title'] for rev in revisions]
        return titles

    def recent_pages_by_interval(self, *args, **kwargs):
        revisions = self.recent_titles_by_interval(*args, **kwargs)
        titles = [rev['title'] for rev in revisions]
        for title in titles:
            yield self.client.pages[title]

    def target(self, name: str):
        """Return the name of a page's redirect target.

        Parameters
        ----------
        1. name : str
            - The name of the redirect page.
        
        Returns
        -------
        - The name of the target page of the redirect.
        """
        if name is None or name == '':
            return None
        return self.client.pages[name].resolve_redirect().name

    def get_simple_pages(self, title_list: List[str], limit: int) -> List[SimplePage]:
        titles_paginated = []
        i = 0
        paginated_element = []
        for title in title_list:
            if i == limit:
                titles_paginated.append(paginated_element)
                paginated_element = []
                i = 0
            paginated_element.append(title)
            i += 1
        ret = []
        titles_paginated.append(paginated_element)
        for query in titles_paginated:
            result = self.client.api('query', prop='revisions', titles='|'.join(query), rvprop='content',
                                     rvslots='main')
            unsorted_pages = []
            for pageid in result['query']['pages']:
                row = result['query']['pages'][pageid]
                name = row['title']
                text = row['revisions'][0]['slots']['main']['*'] if row.get('revisions') else ''
                exists = True if row.get('revisions') else False
                unsorted_pages.append(SimplePage(name=name, text=text, exists=exists))

            # de-alphabetize & sort according to our initial order
            capitalization_corrected_query = []
            for title in query:
                capitalization_corrected_query.append(title[0].upper() + title[1:])
                # We don't know if the : is actually separating a namespace or not. So we'll put both in our lookup for
                # the purpose of re-ordering the response that the api gave us. This is a safe thing to do AS LONG AS
                # both capitalizations didn't previously exist in the original query given to us by the user
                # So along the way just double check that wasn't the case.

                # This might be a bit of a hack but it works out pretty nicely; there's only two possible ways the title
                # could be capitalized, and they end up consecutive in our list (again unless the user specifically
                # specified both separately), so when we reorder later we're guaranteed to look up and find the entry,
                # and have it be in the right order.
                if ':' in title:
                    p = title.index(':')
                    ns_ucfirst_title = title[0].upper() + title[1:p + 1] + title[p + 1].upper() + title[p + 2:]
                    if not any([ns_ucfirst_title in q for q in titles_paginated]):
                        capitalization_corrected_query.append(ns_ucfirst_title)
            unsorted_pages.sort(key=lambda x: capitalization_corrected_query.index(x.name))
            ret += unsorted_pages
        return ret

    def logs_by_interval(self, minutes, offset=0,
                         lelimit="max",
                         leprop='details|type|title|tags', **kwargs):
        now = datetime.datetime.utcnow() - datetime.timedelta(minutes=offset)
        then = now - datetime.timedelta(minutes=minutes)
        logs = self.client.api('query', format='json',
                               list='logevents',
                               #  lestart=now.isoformat(),
                               leend=then.isoformat(),
                               leprop=leprop,
                               lelimit=lelimit,
                               ledir='older',
                               **kwargs
                               )
        return logs['query']['logevents']

    def patrol(self, revid=None, rcid=None, **kwargs):
        if revid is None and rcid is None:
            raise PatrolRevisionNotSpecified
        patrol_token = self.client.get_token('patrol')
        try:
            self.client.api('patrol', revid=revid, rcid=rcid, **kwargs, token=patrol_token)
        except APIError as e:
            if e.code == 'nosuchrevid' or e.code == 'nosuchrcid':
                raise PatrolRevisionInvalid
            self._retry_login_action(self._retry_patrol, 'patrol',
                                     revid=revid, rcid=rcid, token=patrol_token, **kwargs)

    def _retry_patrol(self, **kwargs):
        # one of these two must be provided but not both
        revid = kwargs.pop('revid') if 'revid' in kwargs else None
        rcid = kwargs.pop('rcid') if 'rcid' in kwargs else None

        # token is mandatory
        token = kwargs.pop('token')
        self.client.api('patrol', revid=revid, rcid=rcid, token=token, **kwargs)


    def save(self, page: Page, text, summary=u'', minor=False, bot=True, section=None, log=None, **kwargs):
        """Performs a page edit, retrying the login once if the edit fails due to the user being logged out.

        This function hopefully makes it easy to workaround the lag and frequent login timeouts
        experienced on the Fandom UCP platform compared to Gamepedia Hydra.

        Parameters
        ----------
        1. page : Page
            - The page object of the page to save.
        2.–8.
            - As in mwclient.Page.save().
        """
        try:
            page.edit(text, summary=summary, minor=minor, bot=bot, section=section, **kwargs)
        except ProtectedPageError:
            if log:
                log(exc_info=True, s='Error while saving page {}: Page is protected!'.format(page.name))
            else:
                raise
        except self.write_errors:
            self._retry_login_action(self._retry_save, 'edit', page=page, text=text, summary=summary, minor=minor,
                                     bot=bot, section=section, log=log, **kwargs)

    def _retry_save(self, **kwargs):
        old_page: Page = kwargs.pop('page')
        # recreate the page object so that we're using the new site object, post-relog
        page = self.client.pages[old_page.name]
        text = kwargs.pop('text')
        log = kwargs.pop('log')
        try:
            page.edit(text, **kwargs)
        except ProtectedPageError:
            if log:
                log(exc_info=True, s='Error while saving page {}: Page is protected!'.format(page.name))
            else:
                raise

    def touch(self, page: Page, summary: str = u''):
        """Perform a null-edit on the page.

        The summary will be used in case of edit conflicts, i.e.
        when the null-edit unintentionally reverts someone's edits.
        """
        try:
            page.site = self.client
            if page.exists:
                page.append('', summary, minor=True)
        except self.write_errors:
            self._retry_login_action(self._retry_touch, 'touch', page=page, summary=summary)

    def _retry_touch(self, **kwargs):
        old_page = kwargs['page']
        page = self.client.pages[old_page.name]
        page.touch()

    def purge_title(self, title: str):
        self.purge(self.client.pages[title])

    def purge(self, page: Page):
        try:
            page.site = self.client
            page.purge()
        except self.write_errors:
            self._retry_login_action(self._retry_purge, 'purge', page=page)

    def _retry_purge(self, **kwargs):
        old_page = kwargs['page']
        page = self.client.pages[old_page.name]
        page.purge()


    def move(self, page: Page, new_title, reason='', move_talk=True, no_redirect=False,
             move_subpages=False, ignore_warnings=False):
        try:
            page.site = self.client
            page.move(new_title, reason=reason, move_talk=move_talk, no_redirect=no_redirect,
                      move_subpages=move_subpages, ignore_warnings=ignore_warnings)
        except APIError as e:
            if e.code == 'badtoken':
                self._retry_login_action(self._retry_move, 'move', page=page, new_title=new_title,
                                         reason=reason, move_talk=move_talk, no_redirect=no_redirect,
                                         move_subpages=move_subpages, ignore_warnings=ignore_warnings)
            else:
                raise e

    def _retry_move(self, **kwargs):
        old_page: Page = kwargs.pop('page')
        page = self.client.pages[old_page.name]
        new_title = kwargs.pop('new_title')
        page.move(new_title, **kwargs)


    def delete(self, page: Page, reason='', watch=False, unwatch=False, oldimage=False):
        try:
            page.site = self.client
            page.delete(reason=reason, watch=watch, unwatch=unwatch, oldimage=oldimage)
        except APIError as e:
            if e.code == 'badtoken':
                self._retry_login_action(self._retry_delete, 'delete', page=page, reason=reason,
                                         watch=watch, unwatch=unwatch, oldimage=oldimage)
            else:
                raise e

    def _retry_delete(self, **kwargs):
        old_page: Page = kwargs.pop('page')
        page = self.client.pages[old_page.name]
        page.delete(**kwargs)


    def _retry_login_action(self, f, failure_type, **kwargs):
        was_successful = False
        codes = []
        for retry in range(self.max_retries):
            self.relog()
            # don't sleep at all the first retry, and then increment in retry_interval intervals
            # default interval is 10, default retries is 3
            time.sleep((2 ** retry - 1) * self.retry_interval)
            try:
                f(**kwargs)
                was_successful = True
                break
            except self.write_errors as e:
                if isinstance(e, APIError):
                    codes.append(e.code)
                continue
        if not was_successful:
            raise RetriedLoginAndStillFailed(failure_type, codes)

    def save_title(self, title: str, text, summary=None, minor=False, bot=True, section=None, **kwargs):
        self.save(self.client.pages[title], text,
                  summary=summary, minor=minor, bot=bot, section=section, **kwargs)

    def get_last_rev(self, page: Page, log, query='revid'):
        """Get the latest revision (rev) id or timestamp for a given page.

        Parameters
        ----------
        1. page : mwclient.Page
            - The name of the page to get the revision for.
        """
        try:
            api_result = self.client.api('query', prop='revisions', titles=page.name, rvlimit=1) # https://terraria.gamepedia.com/api.php?action=query&prop=revisions&titles=User:Rye_Greenwood/Sandbox&rvlimit=1
        except KeyboardInterrupt:
            raise
        except:
            log('\n***ERROR*** while getting last revision!')
            log(exc_info=True, s='Error message:\n')
            return None
        page_ids = api_result['query']['pages']
        page_id = -1
        for id in page_ids:
            page_id = id
        try:
            rev = page_ids[page_id]['revisions'][0][query]
        except KeyError: # specified key doesn't exist, either because of invalid "query" arg or nonexistent page
            rev = None

        # rev = [revision for revision in page.revisions(limit=1, prop='ids')][0]['revid'] # this is a shorter alternative, but much much slower, since the limit=1 isn't recognized for some reason, and instead all revs are gathered
        return rev


    def get_last_section(self, page: Page, log, output_as_Wikicode=False, strip=True, anchor=False):
        """Get the heading and wikitext of the last section of the given page.

        Parameters
        ----------
        1. page : mwclient.Page
            - The name of the page to get the section from.
        2. output_as_Wikicode : bool
            - Whether to return the output as a Wikicode object instead of a string.
        3. strip : bool
            - Whether to trim the output (only valid if not output_as_Wikicode).
        4. anchor : bool
            - Whether to include the anchor of the heading in the output.

        Returns
        -------
        Without anchor:
            - (heading, content)
        With anchor:
            - ((headingtitle, headinganchor), content)
        """

        result = None
        try:
            wikitext = mwparserfromhell.parse(page.text())
        except KeyboardInterrupt:
            raise
        except:
            log('\n***ERROR*** while getting last section!')
            log(exc_info=True, s='Error message:\n')
            return None

        # Get heading:
        secs_whead = wikitext.get_sections(include_lead=False)
        if secs_whead: # if there are no sections, just return None
            lastsec = secs_whead[len(secs_whead) - 1]
            heading = None
            anchor_str = None
            for head in lastsec.ifilter_headings():
                heading = head
            if anchor:
                try:
                    api_result = self.client.api('parse', page=page.name, prop='sections')
                except KeyboardInterrupt:
                    raise
                except:
                    log('\n***ERROR*** while getting last section!')
                    log(exc_info=True, s='Error message:\n')
                    return None
                secs = api_result['parse']['sections']
                if len(secs) == 0:
                    return None
                anchor_str = secs[len(secs) - 1]['anchor']

            # Get content:
            secs_nohead = wikitext.get_sections(include_headings=False)
            lastsec = secs_nohead[len(secs_nohead) - 1]
            content = lastsec

            # Format:
            if not output_as_Wikicode:
                content = str(content)
                heading = str(heading)
                if strip:
                    content = content.strip()
                    heading = heading.strip()
            if anchor:
                result = ((heading, anchor_str), content)
            else:
                result = (heading, content)

        return result


    def find_summmary_in_revs(self, page: Page, summary: str, log, user='Ryebot', limit=5, for_undo=False):
        """Get the revision ID of a revision with a specified summary from the specified user in a specified number of last revisions.

        Parameters
        ----------
        1. page : Page
            - The name of the page to operate on.
        2. summary : str
    	    - The edit summary to find.
        3. limit : int
            - The maximum number of revisions to search, starting from the latest
        4. for_undo : bool
            - Whether this method is called for an undo of that revision.
        
        Returns
        -------
        Without ``for_undo``:
            Revision ID.
        With ``for_undo``:
            (revid, prev_revid)
        """

        try:
            api_result = self.client.api('query', prop='revisions', titles=page.name, rvlimit=limit)
        except KeyboardInterrupt:
            raise
        except:
            log('\n***ERROR*** while getting list of revisions!')
            log(exc_info=True, s='Error message:\n')
            return None

        page_id = None
        page_ids = api_result['query']['pages']
        for p_id in page_ids:
            page_id = p_id

        if not page_id:
            return None

        revisions_to_search = page_ids[page_id]['revisions']
        revid = ''
        prev_revid = ''
        for rev in revisions_to_search:
            if rev['comment'] == summary and rev['user'] == user:
                revid = rev['revid']
                prev_revid = rev['parentid']
                break

        if for_undo:
            return (revid, prev_revid)

        return revid


    def namespace_names_to_ids(self, namespaces: list, log):
        """Convert a list of namespace names to their respective IDs.

        Parameters
        ----------
        1. namespaces : list[str]
            - The input list of namespace names.
        
        Returns
        -------
        The list of IDs as strings each.
        """

        result_namespaces = []
        try:
            api_result = self.client.api('query', meta='siteinfo', siprop='namespaces') # https://terraria.gamepedia.com/api.php?action=query&meta=siteinfo&siprop=namespaces
        except KeyboardInterrupt:
            raise
        except:
            log('\n***ERROR*** while list of all namespaces!')
            log(exc_info=True, s='Error message:\n')
            return None

        all_namespaces = api_result['query']['namespaces']
        for ns in all_namespaces:
            if all_namespaces[ns]['*'] in namespaces:
                result_namespaces.append(ns)

        return result_namespaces


    # calls to this function should be able to be replaced with "page.exists"
    def page_exists(self, pagename: str, log):
        """Check whether a page with the specified name exists on the wiki."""
        try:
            api_result = self.client.api('query', prop='info', titles=pagename)
        except KeyboardInterrupt:
            raise
        except:
            log('\n***ERROR*** while checking whether the page "{}" exists!'.format(pagename))
            log(exc_info=True, s='Error message:\n')
            return False
        try:
            if not '-1' in api_result['query']['pages']:
                return True
        except KeyError: # api_result doesn't contain "pages"
            pass

        return False


    def get_current_wiki_name(self):
        """Return the name of the current host, without ``.gamepedia.com`` and ``.fandom.com``, and with ``/<lang>`` appended, if not English."""

        api_result = self.client.api('query', meta='siteinfo', siprop='general')

        sitename = api_result['query']['general']['servername']
        sitename = sitename.replace('.gamepedia.com', '').replace('.fandom.com', '')

        sitelang = api_result['query']['general']['lang']
        if sitelang != "en" and sitelang != '':
            sitename += '/' + sitelang

        return sitename


    def get_current_wiki_user(self):
        """Returns the name of the currently logged in user."""

        api_result = self.client.api('query', meta='userinfo')
        wiki_user = api_result['query']['userinfo']['name']
        return wiki_user


    def get_csrf_token(self, log):
        """Get a CSRF token for a POST request."""

        try:
            api_result = self.client.api('query', meta='tokens')
        except KeyboardInterrupt:
            raise
        except:
            log('\n***ERROR*** while getting CSRF token!')
            log(exc_info=True, s='Error message:\n')
            return None
        token = api_result['query']['tokens']['csrftoken']
        return token


    def api_continue(self, log, action: str, continue_name: str='', i: int=0, **kwargs):
        """
        Provides an API call with recursive, thus unlimited "continue" capability (e.g. for when the number of category members may exceed the bot limit (5000) but we want to get all >5000 of them).
        Returns an array with the contents of each "action" (e.g. "query") call.

        Parameters
        ----------
        1. action : str
            - API action module (e.g. ``query``).
        2. continue_name: str
            - Name of the ``continue`` attribute for the specified action (e.g. ``cmcontinue``). Defaults to first element in the ``continue`` array of the API result.
        3. i: int
            - Internally used by the recursion for debug. Do not use from outside!
        """

        i += 1
        #log('\n[%s] Enter api_continue().' % i)
        try:
            api_result = self.client.api(action, **kwargs)
            #log('[{}] API result: {}'.format(i, api_result))
        except:
            log('\n[{}] ***ERROR*** while executing continued API call (parameters: action=\'{}\', {})'.format(i, action, kwargs))
            log(exc_info=True, s='[{}] Error message:\n'.format(i))
            log('[{}] Aborted API call.'.format(i))
            return

        flag = True
        try:
            _ = api_result['continue']
        except KeyError: # continue doesn't exist
            flag = False
        if flag:
            if not continue_name:
                #log(list(api_result['continue'].keys()))
                continue_name = list(api_result['continue'].keys())[0]
            if api_result['continue'][continue_name]:
                #log('[{}] continue = {}'.format(i, api_result['continue'][continue_name]))
                kwargs.__setitem__(continue_name, api_result['continue'][continue_name]) # add the continue parameter to the next API call
                #log('[{}] Fetching new api result with the following parameters: action=\'{}\', {}'.format(i, action, kwargs))
                next_api_result = self.api_continue(log, action, continue_name, i, **kwargs) # do recursion
                #log('[{}] Received api result from previous call: {}'.format(i, next_api_result))
                if next_api_result:
                    #log('- Append this previous api result to api result from this call:')
                    #log('--- This api result: %s' % [api_result[action]])
                    #log('--- Previous api result that will be appended to above: %s' % next_api_result)

                    if isinstance(next_api_result, dict):
                        next_api_result = [next_api_result]
                    result = next_api_result
                    result.append(api_result[action])
                    #log('- Appended.')
                    #log('[{}] Return:'.format(i))
                    #log('-- %s' % result)
                    #for x in result:
                    #    log('---- %s' % x)
                    return result
                else: # error during API call
                    #log('[%s] Return nothing.\n' % i)
                    return
        else: # reached top of the stack
            #log('[{}] Return {}.\n'.format(i, api_result[action]))
            if i == 1: # still in the first call, no continues were necessary at all
                return [api_result[action]]
            else:
                return api_result[action]


    def redirects_to_inclfragment(self, pagename: str):
        """Similar to ``mwclient.Site.redirects_to()``, but also returns the fragment of the redirect target."""

        api_result = self.client.api('query', prop='pageprops', titles=pagename, redirects='')
        if 'redirects' in api_result['query']:
            for page in api_result['query']['redirects']:
                if page['from'] == pagename:
                    if 'tofragment' in page:
                        return (page['to'], page['tofragment'])
                    else:
                        return (page['to'], None)
                        
        return (None, None)

