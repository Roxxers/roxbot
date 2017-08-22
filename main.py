#!/usr/env python
import logging
import json
import time
import configparser

import discord
from discord.ext import commands

from server_config import ServerConfig

# Sets up Logging that discord.py does on its own
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

settings = configparser.ConfigParser()
settings.read("config/preferences.ini")
command_prefix = settings["Roxbot"]["Command_Prefix"]
token = settings["Roxbot"]["Token"]
owner = settings["Roxbot"]["OwnerID"]

server_config = ServerConfig()

bot = commands.Bot(command_prefix=command_prefix)


@bot.event
async def on_ready():
	print("Client Logged In")
	game = discord.Game(name="Rewriting Moi", type=0)
	await bot.change_presence(game=game)
	print("Game Changed")
	
@bot.event
async def on_server_join(server):
	server_config.servers = server_config.load_config()
	server_config.servers[server.id] = server_config.servers_template["example"]
	server_config.update_config(server_config.servers)

@bot.event
async def on_server_remove(server):
	server_config.servers.pop(server.id)
	server_config.update_config(self.serverconfig)

@bot.event
async def on_message(message):
	# Check for words for reactions and check blacklist
	return await bot.process_commands(message)


@bot.event
async def on_error(error, ctx):
	pass


@bot.event
async def on_command_error(error, ctx):
	pass





bot.run(token)
