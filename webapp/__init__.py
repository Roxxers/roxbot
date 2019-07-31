import os
from flask import Flask
from pony.flask import Pony
import configparser


config = configparser.ConfigParser()
config.read("../roxbot/settings/roxbot.conf")



app = Flask(__name__)
#Pony(app)

OAUTH2_CLIENT_ID = config["webapp"]['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = config["webapp"]['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'
IMAGE_BASE_URL = "https://cdn.discordapp.com/"


app.debug = True
app.use_reloader=False
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
app.config['TEMPLATES_AUTO_RELOAD'] = False

from webapp import routes, oauth



