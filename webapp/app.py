from quart import Quart
from webapp.discord_client import bot



class RoxbotWebapp(Quart):
    def __init__(self, *args, **kwargs):
        self.discord_client = bot.client
        super().__init__(*args, **kwargs)