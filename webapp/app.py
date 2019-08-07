from quart import Quart
from webapp import _discord


class RoxbotWebapp(Quart):
    def __init__(self, *args, **kwargs):
        self.discord_client = None
        self.discord_accessor = _discord.bot
        super().__init__(*args, **kwargs)
