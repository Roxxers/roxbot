import requests
from config.server_config import ServerConfig

import discord
from discord.ext.commands import bot, group


class Trivia:
	"""
	Trivia is based off the lovely https://opentdb.com made by PixelTail Games.
	"""
	def __init__(self, bot_client):
		self.bot = bot_client
		self.con = ServerConfig()
		self.serverconfig = self.con.servers




def setup(Bot):
	Bot.add_cog(Trivia(Bot))