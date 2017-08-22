#!/usr/env python
import logging

import discord
from discord.ext import commands

from server_config import ServerConfig
import load_config

# Sets up Logging that discord.py does on its own
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


server_config = ServerConfig()
bot = commands.Bot(command_prefix=load_config.command_prefix, description=load_config.description)


@bot.event
async def on_ready():
	server_config.error_check(bot.servers)
	print("Client Logged In")
	bot.owner = load_config.owner
	print("Cogs Loaded:")
	for cog in load_config.cogslist:
		bot.load_extension(cog)
		print(cog)
	
	# Testing Code
	game = discord.Game(name="Rewriting Moi for v{}".format(load_config.version), type=0)
	await bot.change_presence(game=game)
	print("Game Changed")


@bot.event
async def on_server_join(server):
	server_config.servers = server_config.load_config()
	server_config.servers[server.id] = server_config.servers_template["example"]
	server_config.update_config(server_config.servers)


@bot.event
async def on_server_remove(server):
	server_config.servers = server_config.load_config()
	server_config.servers.pop(server.id)
	server_config.update_config(server_config.servers)


@bot.event
async def on_message(message):
	# TODO: Check for words for reactions and check blacklist
	return await bot.process_commands(message)


@bot.event
async def on_error(error, ctx):
	pass


@bot.event
async def on_command_error(error, ctx):
	pass


bot.run(load_config.token)
