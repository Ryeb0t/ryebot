import mwparserfromhell

from custom_mwclient.auth_credentials import AuthCredentials
from custom_mwclient.fandom_client import FandomClient


def template_str_to_object(template_str: str):
    """Turn the input string into an mwparserfromhell.Template object.

    It is assumed the string does contain a template and only consists of that template.
    """

    wikitext = mwparserfromhell.parse(template_str)
    for template in wikitext.filter_templates():
        return template
    return None


def login_to_wiki(targetwiki: str, credentials_file: str, return_log=False, log=None):
    """Basic login to a wiki.

    Parameters
    ----------
    1. targetwiki : str
        - The name of the wiki, e.g. `terrariamods` or `terraria/de`.
    2. credentials_file : str
        - Path to the file that contains the credentials for the target user.
    3. return_log : bool
        - Whether to return a log of the login actions.
        Will log on its own (using the function provided in the `log` parameter)
        if set to `False`.

    Returns
    -------
    1. Without `return_log`:
        - site
    2. With `return_log`:
        - (site, logstr)
    """

    # --- do login ---
    creds = AuthCredentials(credentials_file)

    try:
        targetwiki_base, targetwiki_lang = targetwiki.split('/')
        has_lang = True
    except ValueError:
        # the targetwiki string has more or fewer than one slash character, so don't use a language
        has_lang = False

    if has_lang:
        site = FandomClient(credentials=creds, wiki=targetwiki_base, lang=targetwiki_lang)
    else:
        site = FandomClient(credentials=creds, wiki=targetwiki)

    # -- validate wikiname post-login ---
    wiki_id = site.get_current_wiki_name()
    if wiki_id != targetwiki:
        raise Exception(f'Target wiki was "{targetwiki}", current wiki is "{wiki_id}"!')

    # --- validate username post-login ---
    expected_user = creds.username.split('@')[0]
    # expected user comes with underscores instead of spaces;
    # get_current_wiki_user returns the name with spaces, so aligning them both here
    wiki_user = site.get_current_wiki_user().replace(" ", "_")
    if wiki_user != expected_user:
        raise Exception(f'Target user was "{expected_user}", current user is "{wiki_user}"!')

    # --- validations were successful ---
    logstr = f'Logged in to wiki "{wiki_id}" with user "{wiki_user}".'

    if return_log:
        return (site, logstr)
    if log:
        log(logstr)
    return site
