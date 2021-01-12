import configparser
import os
from os.path import dirname, realpath, join


ROOT_DIR: str = dirname(dirname(realpath(__file__)))

config = configparser.ConfigParser()
config.read('config.ini')

DEVEL_MODE = config['DEFAULT']['mode'] == "development"

SCOPES = [
    config['SCOPES'][key]
    for key in config['SCOPES']
    if key != "mode"
]

SECTION = "DEVELOPMENT" if DEVEL_MODE else "PRODUCTION"
CLIENT_SECRET = join(ROOT_DIR, config[SECTION]['client_secret'])
REDIRECT_URI = config[SECTION]['redirect_uri']
MAX_RESULTS = config[SECTION]['fetch_size']

def onStartUp():
    if DEVEL_MODE:
        os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')

# Raise custom exceptions if not found