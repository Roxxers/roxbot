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


import os
import string
import typing
import logging
import asyncio
import datetime
import youtube_dl

import roxbot

import discord
from discord.ext import commands


class ErrorHandling:

	COMMANDNOTFOUND = "That Command doesn't exist."
	COMMANDONCOOLDOWN = "This command is on cooldown, please wait {:.2f} seconds before trying again."
	CHECKFAILURE = "You do not have permission to do this. Back off, thot!"
	TOOMANYARGS = "Too many arguments given."
	DISABLEDCOMMAND = "This command is disabled."
	COGSETTINGDISABLED = "{} is disabled on this server."
	NODMS = "This command cannot be used in private messages."

	YTDLDOWNLOADERROR = "Video could not be downloaded: {}"

	def __init__(self, bot_client):
		self.bot = bot_client
		self.dev = roxbot.dev_mode

	async def on_command_error(self, ctx, error):
		if self.dev:
			raise error
		else:
			# UserError warning section
			user_errors = (commands.MissingRequiredArgument, commands.BadArgument,
						   commands.TooManyArguments, roxbot.UserError)

			if isinstance(error, user_errors):
				embed = discord.Embed(colour=roxbot.EmbedColours.orange)
				if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument, roxbot.UserError)):
					embed.description = error.args[0]
				elif isinstance(error, commands.TooManyArguments):
					embed.description = self.TOOMANYARGS
				return await ctx.send(embed=embed)

			# ActualErrorHandling
			embed = discord.Embed()
			if isinstance(error, commands.NoPrivateMessage):
				embed.description = self.NODMS
				logging.INFO(embed.description)
			elif isinstance(error, commands.DisabledCommand):
				embed.description = self.DISABLEDCOMMAND
				logging.INFO(embed.description)
			elif isinstance(error, roxbot.CogSettingDisabled):
				embed.description = self.COGSETTINGDISABLED.format(error.args[0])
				logging.INFO(embed.description)
			elif isinstance(error, commands.CommandNotFound):
				try:
					# Sadly this is the only part that makes a cog not modular. I have tried my best though to make it usable without the cog.
					cc = roxbot.guild_settings.get(ctx.guild)["custom_commands"]
					is_custom_command = bool(ctx.invoked_with in cc["1"] or ctx.invoked_with in cc["2"])
					is_emoticon_face = bool(any(x in string.punctuation for x in ctx.message.content.strip(ctx.prefix)[0]))
					is_too_short = bool(len(ctx.message.content) <= 2)
					if is_custom_command or is_emoticon_face or is_too_short:
						embed = None
					else:
						embed.description = self.COMMANDNOTFOUND
						logging.INFO(embed.description)
				except (KeyError, AttributeError):
					# KeyError for cog missing, AttributeError if a command invoked via DM
					embed.description = self.COMMANDNOTFOUND
					logging.INFO(embed.description)
			elif isinstance(error, commands.BotMissingPermissions):
				embed.description = "{}".format(error.args[0].replace("Bot", "Roxbot"))
				logging.INFO(embed.description)
			elif isinstance(error, commands.MissingPermissions):
				embed.description = "{}".format(error.args[0])
				logging.INFO(embed.description)
			elif isinstance(error, commands.CommandOnCooldown):
				embed.description = self.COMMANDONCOOLDOWN.format(error.retry_after)
				logging.INFO(embed.description)
			elif isinstance(error, (commands.CheckFailure, commands.NotOwner)):
				embed.description = self.CHECKFAILURE
				logging.INFO(embed.description)

			elif isinstance(error, commands.CommandInvokeError):
				# YOUTUBE_DL ERROR HANDLING
				if isinstance(error.original, youtube_dl.utils.GeoRestrictedError):
					embed.description = self.YTDLDOWNLOADERROR.format("Video is GeoRestricted.")
					logging.INFO(embed.description)
				elif isinstance(error.original, youtube_dl.utils.DownloadError):
					embed.description = self.YTDLDOWNLOADERROR.format(error.original.exc_info[1])
					logging.INFO(embed.description)

				# Final catches for errors undocumented.
				else:
					logging.ERROR(str(error))
					embed = discord.Embed(title='Command Error', colour=roxbot.EmbedColours.dark_red)
					embed.description = str(error)
					embed.add_field(name='User', value=ctx.author)
					embed.add_field(name='Message', value=ctx.message.content)
					embed.timestamp = datetime.datetime.utcnow()
			elif isinstance(error, commands.CommandError):
				embed.description = "Error: {}".format(error.args[0])
				logging.ERROR(embed.description)
			else:
				logging.ERROR(str(error))

			if embed:
				embed.colour = roxbot.EmbedColours.dark_red
				await ctx.send(embed=embed)


class Logging:
	"""Cog that deals with internal logging with Roxbot that is posted in Discord."""
	def __init__(self, bot_client):
		self.bot = bot_client

		self.settings = {
			"logging": {
				"enabled": 0,
				"convert": {"enabled": "bool", "channel": "channel"},
				"channel": 0
			}
		}

		self.bot.add_listener(self.cleanup_logging_settings, "on_guild_channel_delete")
		self.bot.add_listener(self.log_member_join, "on_member_join")
		self.bot.add_listener(self.log_member_remove, "on_member_remove")

	@staticmethod
	async def cleanup_logging_settings(channel):
		"""Cleans up settings on removal of stored IDs."""
		settings = roxbot.guild_settings.get(channel.guild)
		r_logging = settings["logging"]
		if channel.id == r_logging["channel"]:
			r_logging["channel"] = 0
			settings.update(r_logging, "logging")

	async def log_member_join(self, member):
		r_logging = roxbot.guild_settings.get(member.guild)["logging"]
		if r_logging["enabled"]:
			channel = self.bot.get_channel(r_logging["channel"])
			embed = discord.Embed(title="{} joined the server".format(member), colour=roxbot.EmbedColours.pink)
			embed.add_field(name="ID", value=member.id)
			embed.add_field(name="Mention", value=member.mention)
			embed.add_field(name="Date Account Created", value=roxbot.datetime_formatting.format(member.created_at))
			embed.add_field(name="Date Joined", value=roxbot.datetime_formatting.format(member.joined_at))
			embed.set_thumbnail(url=member.avatar_url)
			return await channel.send(embed=embed)

	async def log_member_remove(self, member):
		# TODO: Add some way of detecting whether a user left/was kicked or was banned.
		r_logging = roxbot.guild_settings.get(member.guild)["logging"]
		if r_logging["enabled"]:
			channel = self.bot.get_channel(r_logging["channel"])
			embed = discord.Embed(description="{} left the server".format(member), colour=roxbot.EmbedColours.pink)
			return await channel.send(embed=embed)

	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	@commands.command(aliases=["log"])
	async def logging(self, ctx, setting, *, channel: typing.Optional[discord.TextChannel] = None):
		"""Edits the logging settings.

		Options:
			enable/disable: Enable/disables logging.
			channel: sets the channel.
		"""

		setting = setting.lower()
		settings = roxbot.guild_settings.get(ctx.guild)

		if setting == "enable":
			settings["logging"]["enabled"] = 1
			await ctx.send("'logging' was enabled!")
		elif setting == "disable":
			settings["logging"]["enabled"] = 0
			await ctx.send("'logging' was disabled :cry:")
		elif setting == "channel":
			if not channel:
				channel = ctx.channel
			settings["logging"]["channel"] = channel.id
			await ctx.send("{} has been set as the logging channel!".format(channel.mention))
		else:
			return await ctx.send("No valid option given.")
		return settings.update(settings["logging"], "logging")


class Core(ErrorHandling, Logging):
	"""Core bot cog. Includes management commands, logging, error handling, and backups."""
	def __init__(self, bot_client):
		self.bot = bot_client
		super().__init__(self.bot)

		# Backup setup
		if roxbot.backup_enabled:
			self.backup_task = self.bot.loop.create_task(self.auto_backups())

	#############
	#  Backups  #
	#############

	async def auto_backups(self):
		await self.bot.wait_until_ready()
		raw_settings = {}
		for guild in self.bot.guilds:
			directory = os.listdir('roxbot/settings/servers/{}'.format(guild.id))
			raw_settings = {**raw_settings, **roxbot.guild_settings._open_config(guild, directory)}
		while not self.bot.is_closed():
			current_settings = {}
			for guild in self.bot.guilds:
				directory = os.listdir('roxbot/settings/servers/{}'.format(guild.id))
				current_settings = {**current_settings, **roxbot.guild_settings._open_config(guild, directory)}
			if raw_settings != current_settings:
				raw_settings = current_settings
				time = datetime.datetime.now()
				roxbot.guild_settings.backup("{:%Y.%m.%d %H:%M:%S} Auto Backup".format(time))
			await asyncio.sleep(roxbot.backup_rate)

	@commands.command(enabled=roxbot.backup_enabled)
	@commands.is_owner()
	async def backup(self, ctx):
		"""Manually create a backup of the settings."""
		time = datetime.datetime.now()
		filename = "{:%Y.%m.%d %H:%M:%S} Manual Backup".format(time)
		roxbot.guild_settings.backup(filename)
		return await ctx.send("Settings file backed up as a folder named '{}".format(filename))

	############################
	#  Bot Managment Commands  #
	############################

	@commands.command()
	@commands.is_owner()
	async def blacklist(self, ctx, option):
		"""
		Add or remove users to the blacklist. Blacklisted users are forbidden from using bot commands.
		Usage:
			;blacklist [add|+ OR remove|-] @user#0000
		OWNER OR ADMIN ONLY
		"""
		# TODO: Make this better instead of relying on mentions
		blacklist_amount = 0
		mentions = ctx.message.mentions

		if not mentions:
			return await ctx.send("You didn't mention anyone")

		if option not in ['+', '-', 'add', 'remove']:
			return await ctx.send('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

		for user in mentions:
			if user.id == roxbot.owner:
				await ctx.send("The owner cannot be blacklisted.")
				mentions.remove(user)

		if option in ['+', 'add']:
			with open("roxbot/blacklist.txt", "r") as fp:
				for user in mentions:
					for line in fp.readlines():
						if user.id + "\n" in line:
							mentions.remove(user)

			with open("roxbot/blacklist.txt", "a+") as fp:
				lines = fp.readlines()
				for user in mentions:
					if user.id not in lines:
						fp.write("{}\n".format(user.id))
						blacklist_amount += 1
			return await ctx.send('{} user(s) have been added to the blacklist'.format(blacklist_amount))

		elif option in ['-', 'remove']:
			with open("roxbot/blacklist.txt", "r") as fp:
				lines = fp.readlines()
			with open("roxbot/blacklist.txt", "w") as fp:
				for user in mentions:
					for line in lines:
						if str(user.id) + "\n" != line:
							fp.write(line)
						else:
							fp.write("")
							blacklist_amount += 1
				return await ctx.send('{} user(s) have been removed from the blacklist'.format(blacklist_amount))

	@commands.command(aliases=["setavatar"])
	@commands.is_owner()
	async def changeavatar(self, ctx, url=None):
		"""
		Changes the bot's avatar. Can't be a gif.
		Usage:
			;changeavatar [url]
		Attaching a file and leaving the url parameter blank also works.
		"""
		avaimg = 'avaimg'
		if ctx.message.attachments:
			await ctx.message.attachments[0].save(avaimg)
		else:
			url = url.strip('<>')
			await roxbot.http.download_file(url, avaimg)
		with open(avaimg, 'rb') as f:
			await self.bot.user.edit(avatar=f.read())
		os.remove(avaimg)
		await asyncio.sleep(2)
		return await ctx.send(":ok_hand:")

	@commands.command(aliases=["nick", "nickname"])
	@commands.is_owner()
	@commands.bot_has_permissions(change_nickname=True)
	async def changenickname(self, ctx, *, nick=None):
		"""Changes the bot's nickname in the guild.
		Usage:
			;nickname [nickname]"""
		await ctx.guild.me.edit(nick=nick, reason=";nick command invoked.")
		return await ctx.send(":thumbsup:")

	@commands.command(aliases=["activity"])
	@commands.is_owner()
	async def changeactivity(self, ctx, *, game: str):
		"""Changes the "playing" status of the bot.
		Usage:
			;changeactivity` [game]"""
		if game.lower() == "none":
			game = None
		else:
			game = discord.Game(game)
		await self.bot.change_presence(activity=game)
		return await ctx.send(":ok_hand: Activity set to {}".format(str(game)))

	@commands.command(aliases=["status"])
	@commands.is_owner()
	async def changestatus(self, ctx, status: str):
		"""Changes the status of the bot.
		Usage:
			;changesatus [game]"""
		status = status.lower()
		if status == 'offline' or status == 'invisible':
			discord_status = discord.Status.invisible
		elif status == 'idle':
			discord_status = discord.Status.idle
		elif status == 'dnd':
			discord_status = discord.Status.dnd
		else:
			discord_status = discord.Status.online
		await self.bot.change_presence(status=discord_status)
		await ctx.send("**:ok:** Status set to {}".format(discord_status))

	@staticmethod
	def _parse_setting(ctx, settings_to_copy, raw=False):
		settingcontent = ""
		setting = settings_to_copy.copy()
		convert = setting.get("convert", None)

		if convert is not None and not raw:
			for x in convert.keys():
				converter = None
				if convert[x] == "bool":
					if setting[x] == 0:
						setting[x] = False
					else:
						setting[x] = True
				elif convert[x] == "channel":
					converter = ctx.guild.get_channel
				elif convert[x] == "role":
					converter = ctx.guild.get_role
				elif convert[x] in ("user", "member"):
					converter = ctx.guild.get_member
				elif convert[x] == "hide":
					converter = None
					setting[x] = "This is hidden. Please use other commands to get this data."
				else:
					converter = None

				if converter:
					if isinstance(setting[x], list):
						if len(setting[x]) >= 60:
							setting[x] = "There is too many {}s to display. Please use other commands to get this data.".format(convert[x])
						else:
							new_entries = []
							for entry in setting[x]:
								try:
									new_entries.append(converter(entry))
								except AttributeError:
									new_entries.append(entry)
							setting[x] = new_entries
					else:
						try:
							setting[x] = converter(setting[x])
						except AttributeError:
							pass

		for x in setting.items():
			if x[0] != "convert":
				settingcontent += str(x).strip("()") + "\n"
		return settingcontent

	@commands.guild_only()
	@commands.command(aliases=["printsettingsraw"])
	@commands.has_permissions(manage_guild=True)
	async def printsettings(self, ctx, option=None):
		"""OWNER OR ADMIN ONLY: Prints the servers settings file."""
		config = roxbot.guild_settings.get(ctx.guild)
		settings = dict(config.settings.copy())  # Make a copy of settings so we don't change the actual settings.
		paginator = commands.Paginator(prefix="```py")
		paginator.add_line("{} settings for {}.\n".format(self.bot.user.name, ctx.message.guild.name))
		if option in settings:
			raw = bool(ctx.invoked_with == "printsettingsraw")
			settingcontent = self._parse_setting(ctx, settings[option], raw=raw)
			paginator.add_line("@{}".format(option))
			paginator.add_line(settingcontent)
			for page in paginator.pages:
				await ctx.send(page)
		else:
			for setting in settings:
				raw = bool(ctx.invoked_with == "printsettingsraw")
				settingcontent = self._parse_setting(ctx, settings[setting], raw=raw)
				paginator.add_line("@{}".format(setting))
				paginator.add_line(settingcontent)
			for page in paginator.pages:
				await ctx.send(page)

	@commands.command()
	@commands.is_owner()
	async def shutdown(self, ctx):
		"""Shuts down the bot."""
		await ctx.send(":wave:")
		await self.bot.logout()


def setup(bot_client):
	bot_client.add_cog(Core(bot_client))
