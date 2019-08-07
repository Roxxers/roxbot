
from webapp.app import RoxbotWebapp

app = RoxbotWebapp(__name__)

app.config.from_pyfile('config.py')

app.discord_accessor.start()
app.discord_client = app.discord_accessor.client
app.debug = True
app.use_reloader=False


from webapp import routes, oauth, _discord, config



