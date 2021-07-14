import os.path

PATHS = { 'localdata':'', 'wikis':'', 'global_config':''}

PATHS['localdata'] = os.path.join(os.path.expanduser('~'), 'ryebot', 'localdata')

PATHS['venv'] = os.path.join(PATHS['localdata'], '.ryebotvenv')
PATHS['wikis'] = os.path.join(PATHS['localdata'], 'wikis')
PATHS['global_config'] = os.path.join(PATHS['localdata'], 'global_config')