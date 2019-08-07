import os
import configparser

config = configparser.ConfigParser()
config.read("../roxbot.conf")

OAUTH2_CLIENT_ID = config["webapp"]['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = config["webapp"]['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'
IMAGE_BASE_URL = "https://cdn.discordapp.com/"


SECRET_KEY = OAUTH2_CLIENT_SECRET
TEMPLATES_AUTO_RELOAD = False

DISCORD_TOKEN = config["Tokens"]["Discord"]
INSTANCE_OWNER_ID = config["Roxbot"]["OwnerID"]