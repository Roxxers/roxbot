#!/usr/env python

import configparser
from discord.ext import commands

settings = configparser.ConfigParser()
settings.read("config/preferences.ini")
command_prefix = settings["Roxbot"]["Command_Prefix"]
token = settings["Roxbot"]["Token"]

bot = commands.Bot(command_prefix=command_prefix)

@bot.event
async def on_ready():
	print("Client Logged In")

bot.run(token)