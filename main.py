#!/usr/env python3

import time
import logging
import os.path
import datetime
import discord
from discord.ext import commands
import load_config
from config.server_config import ServerConfig


# Sets up Logging that discord.py does on its own
logger = logging.getLogger('discord')
logger.setLevel(logging.WARN)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

server_config = ServerConfig()
bot = commands.Bot(
	command_prefix=load_config.command_prefix,
	description=load_config.__description__,
	owner_id=load_config.owner,
	activity=discord.Game(name="v{}".format(load_config.__version__), type=0)
)

def blacklisted(user):
	with open("config/blacklist.txt", "r") as fp:
		for line in fp.readlines():
			if user.id+"\n" == line:
				return True
	return False

@bot.event
async def on_ready():
	server_config.error_check(bot.guilds)
	print("Discord.py version: " + discord.__version__)
	print("Client logged in\n")

	print("Cogs Loaded:")
	for cog in load_config.cogs:
		bot.load_extension(cog)
		print(cog)
	print("")

	print("Servers I am currently in:")
	for server in bot.guilds:
		print(server)
	print("")


@bot.event
async def on_server_join(server):
	server_config.servers = server_config.load_config()
	server_config.servers[str(server.id)] = server_config.servers_template["example"]
	server_config.update_config(server_config.servers)


@bot.event
async def on_server_remove(server):
	server_config.servers = server_config.load_config()
	server_config.servers.pop(str(server.id))
	server_config.update_config(server_config.servers)


@bot.event
async def on_message(message):
	if blacklisted(message.author):
		return
	return await bot.process_commands(message)

@bot.command()
async def about(ctx):
	"""
	Outputs info about RoxBot, showing uptime, how to report issues, what settings where set in prefs.ini and credits.
	"""
	owner = bot.get_user(load_config.owner)
	em = discord.Embed(title="About Roxbot", colour=load_config.embedcolour, description=load_config.__description__)
	em.set_thumbnail(url=bot.user.avatar_url)
	em.add_field(name="Command Prefix", value=load_config.command_prefix)
	em.add_field(name="Owner", value=str(owner))
	em.add_field(name="Owner ID", value=load_config.owner)
	em.add_field(name="Bot Version", value=load_config.__version__)
	em.add_field(name="Author", value=load_config.__author__)
	em.add_field(name="Discord.py version", value=discord.__version__)
	em.set_footer(text="RoxBot is licensed under the MIT License")

	# Do time calc late in the command so that the time returned is closest to when the message is received
	uptimeflo = time.time() - start_time
	uptime = str(datetime.timedelta(seconds=uptimeflo))
	em.add_field(name="Current Uptime", value=str(uptime.split(".")[0]))

	return await ctx.channel.send(embed=em)


if __name__ == "__main__":
	# Pre-Boot checks
	if not os.path.isfile("settings/preferences.ini"):
		print(
			"PREFERENCE FILE MISSING. Something has gone wrong. Please make sure there is a file called 'preferences.ini' in the settings folder")
		exit(0)

	if not os.path.isfile("config/servers.json"):
		with open("config/servers.json", "w+") as fp:
			fp.write("{}")

	start_time = time.time()
	bot.load_extension("config.settings")
	bot.load_extension("err_handle")
	bot.run(load_config.token)
