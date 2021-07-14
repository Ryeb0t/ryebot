import os.path

from setuptools import find_packages, setup

# +++++++++++++++++++++++++++++++++
# ++  Metadata definition start  ++
# +++++++++++++++++++++++++++++++++

PACKAGE_NAME = 'ryebot'
DESCRIPTION = 'Command line tool to control automated actions on Gamepedia/Fandom wikis'
AUTHOR = 'Rye Greenwood'
AUTHOR_EMAIL = ''
LICENSE = 'MIT'
URL = 'https://github.com/Ryeb0t/ryebot'
PYTHON_VERSION = '>=3.8.0'
REQUIREMENTS = [
    'mwclient',
    'mwparserfromhell',
    'click>=8.0.0',
    'psutil',
    'logging',
    'python-daemon'
]
# command that will be used to execute the program from the command line
ENTRYPOINT_COMMAND = 'ryebot'

# +++++++++++++++++++++++++++++++++
# ++   Metadata definition end   ++
# +++++++++++++++++++++++++++++++++


# load long description from readme.md
try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = DESCRIPTION # fallback to short description if no README.md available

# load version from _version.py as dictionary
versioninfo = {}
try:
    with open(os.path.join('.', 'ryebot', '_version.py')) as f:
        exec(f.read(), versioninfo)
except FileNotFoundError:
    versioninfo['__version__'] = '0.0.0'
else:
    if '__version__' not in versioninfo:
        raise RuntimeError('Invalid format of _version.py! Couldn\'t find a "__version__" key.')

# set all metadata
setup(
    name=PACKAGE_NAME,
    version=versioninfo['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    packages=find_packages(),
    python_requires=PYTHON_VERSION,
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            ENTRYPOINT_COMMAND + ' = ryebot.bot.console_entry_point:main'
        ]
    }
)
