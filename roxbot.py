#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017-2018 Roxanne Gibson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import time
import logging
import os.path
import datetime
import traceback

import discord
from discord.ext import commands

import roxbot
from roxbot import guild_settings as gs


# Sets up Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='roxbot.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(
	command_prefix=roxbot.command_prefix,
	description=roxbot.__description__,
	owner_id=roxbot.owner,
	activity=discord.Game(name="v{}".format(roxbot.__version__), type=0),
	case_insensitive=True
)


@bot.event
async def on_ready():
	# Load Roxbots inbuilt cogs and settings
	print("Loading Bot internals...")

	bot.load_extension("roxbot.core")
	print("core.py Loaded")

	print("")
	print("Discord.py version: " + discord.__version__)
	print("Client logged in\n")

	# Load Extension Cogs
	print("Cogs Loaded:")
	for cog in roxbot.cogs:
		try:
			bot.load_extension(cog)
			print(cog.split(".")[2])
		except ImportError:
			print("{} FAILED TO LOAD. MISSING REQUIREMENTS".format(cog.split(".")[2]))
	print("")

	# this is so if we're added to a server while we're offline we deal with it
	roxbot.guild_settings.error_check(bot.guilds, bot.cogs)

	print("Guilds I'm currently in:")
	for guild in bot.guilds:
		print(guild)
	print("")


@bot.event
async def on_guild_join(guild):
	gs.add_guild(guild, bot.cogs)


@bot.event
async def on_guild_remove(guild):
	gs.remove_guild(guild)


@bot.event
async def on_error(event, *args, **kwargs):
	if roxbot.dev_mode:
		traceback.print_exc()
	else:
		logging.exception(event)


@bot.check
def check_blacklist(ctx):
	"""Adds global check to the bot to check for a user being blacklisted."""
	return not roxbot.blacklisted(ctx.author)


@bot.command()
async def about(ctx):
	"""
	Outputs info about RoxBot, showing up time, how to report issues, what settings where set in prefs.ini and credits.
	"""
	owner = bot.get_user(roxbot.owner)
	em = discord.Embed(title="About Roxbot", colour=roxbot.EmbedColours.pink, description=roxbot.__description__)
	em.set_thumbnail(url=bot.user.avatar_url)
	em.add_field(name="Command Prefix", value=roxbot.command_prefix)
	em.add_field(name="Owner", value=str(owner))
	em.add_field(name="Owner ID", value=roxbot.owner)
	em.add_field(name="Bot Version", value=roxbot.__version__)
	em.add_field(name="Author", value=roxbot.__author__)
	em.add_field(name="Discord.py version", value=discord.__version__)
	em.set_footer(text="RoxBot is licensed under the MIT License")

	# Do time calc late in the command so that the time returned is closest to when the message is received
	uptimeflo = time.time() - start_time
	uptime = str(datetime.timedelta(seconds=uptimeflo))
	em.add_field(name="Current Uptime", value=str(uptime.split(".")[0]))

	return await ctx.channel.send(embed=em)


@commands.command(pass_context=False, hidden=True)
async def settings():
	# This is to block any customcommand or command from being made with the same name.
	# This is to avoid conflicts with the internal settings system.
	raise commands.CommandNotFound()

if __name__ == "__main__":
	# Pre-Boot checks
	if not os.path.isfile("roxbot/settings/preferences.ini"):
		print("PREFERENCE FILE MISSING. Please make sure there is a file called 'preferences.ini' in the settings folder")
		exit(0)

	start_time = time.time()
	bot.run(roxbot.token)
