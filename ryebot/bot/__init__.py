import os.path

PATHS = {}

PATHS['base'] = os.path.join(os.path.expanduser('~'), 'ryebot')

PATHS['package'] = os.path.join(PATHS['base'], 'ryebot')

PATHS['localdata'] = os.path.join(PATHS['base'], 'localdata')

PATHS['venv'] = os.path.join(PATHS['localdata'], '.ryebotvenv')
PATHS['wikis'] = os.path.join(PATHS['localdata'], 'wikis')
PATHS['global_config'] = os.path.join(PATHS['localdata'], 'global_config')