import os

from ryebot.bot import PATHS
from ryebot.custom_utils.wiki_util import login_to_wiki


def login(wikiname: str, username: str = 'bot', **kwargs):

    file_pattern = 'wiki_account_{}.json'
    credentials_file = os.path.join(PATHS['global_config'], file_pattern.format(username.lower()))

    return login_to_wiki(wikiname, credentials_file, **kwargs)


def get_local_wikis():
    """Return a list of registered wikis.

    Registered wikis are those that have a subdirectory in the `localdata/wikis`
    directory, i.e., that the bot has access to.
    """

    local_wikis = []
    for wikiname in os.listdir(PATHS['wikis']):
        for language_variant in os.listdir(os.path.join(PATHS['wikis'], wikiname)):
            if language_variant == 'MAIN':
                local_wikis.append(wikiname)
            else:
                local_wikis.append(wikiname + '/' + language_variant)

    return local_wikis


def get_wiki_directory_from_name(wikiname: str):
    parts = wikiname.count('/') + 1
    if parts == 2:
        # wikiname is e.g. "terraria/de", so return ("terraria", "de")
        basedirname, subdirname = wikiname.split('/')
    elif parts == 1:
        # wikiname is e.g. "terraria", so return ("terraria", "MAIN")
        basedirname = wikiname
        subdirname = 'MAIN'
    else:
        raise ValueError(f'Wiki name "{wikiname}" contains more than one slash; '
            'expected is one or no slash!')
    return (basedirname, subdirname)


def get_wiki_directory_from_path(path: str):
    subpath = []
    basepath = path
    # e.g. start with basepath='/pathswikis/terraria/MAIN/some.file'

    while basepath != PATHS['wikis']:
        subpath.append(os.path.basename(basepath))
        basepath = os.path.dirname(basepath)
    # e.g. subpath would now be ['some.file', 'MAIN', 'terraria']

    if len(subpath) < 2:
        raise ValueError(f'Cannot get the wiki directory from the path "{path}"!')

    # e.g. return ('MAIN', 'terraria')
    return (subpath[-1], subpath[-2])


def get_wiki_name_from_directory(basedir: str, subdir: str):
    if subdir != 'MAIN':
        basedir += '/' + subdir
    return basedir


def get_wiki_name_from_path(path: str):
    return get_wiki_name_from_directory(*get_wiki_directory_from_path(path))

