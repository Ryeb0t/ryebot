import mwparserfromhell

from custom_mwclient.auth_credentials import AuthCredentials
from custom_mwclient.fandom_client import FandomClient


def template_str_to_object(template_str: str):
    """Turns the input string into an mwparserfromhell.Template object.
    
    It is assumed the string does contain a template and only consists of that template.
    """

    wikitext = mwparserfromhell.parse(template_str)
    for template in wikitext.filter_templates():
        return template
    return


def login_to_wiki(targetwiki: str, username='bot', return_log=False, log=None):
    """Basic login to a wiki.

    Parameters
    ----------
    1. targetwiki : str
        - The name of the wiki, e.g. ``terrariamods`` or ``terraria/de``.
    2. username : str
        - Whether to log in as Ryebot (``bot``) or Rye Greenwood (``me``).
    3. return_log : bool
        - Whether to return a log of the login actions. Will log on its own (using the function provided in the ``log`` parameter) if set to ``False``.
    
    Returns
    -------
    1. Without ``return_log``:
        - site
    2. With ``return_log``:
        - (site, logstr)
    """

    # --- do login ---
    creds = AuthCredentials(user_name=username)
    site = FandomClient(wiki=targetwiki, credentials=creds)

    # -- validate wikiname post-login ---
    wiki_id = site.get_current_wiki_name()
    if wiki_id != targetwiki:
        raise Exception('Target wiki was "{}", current wiki is "{}"!'.format(targetwiki, wiki_id))

    # --- validate username post-login ---
    expected_user = creds.username.split('@')[0]
    # expected user comes with underscores instead of spaces;
    # get_current_wiki_user returns the name with spaces, so aligning them both here
    wiki_user = site.get_current_wiki_user().replace(" ", "_")
    if wiki_user != expected_user:
        raise Exception('Target user was "{}", current user is "{}"!'.format(expected_user, wiki_user))

    # --- validations were successful ---
    logstr = 'Logged in to wiki "{}" with user "{}".'.format(wiki_id, wiki_user)

    if return_log:
        return (site, logstr)
    elif log:
        log(logstr)
    return site
