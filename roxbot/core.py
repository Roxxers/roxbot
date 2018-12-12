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


import asyncio
import datetime
import os
import string
import typing

import discord
import youtube_dl
from discord.ext import commands

import roxbot


class Roxbot(commands.Bot):
	"""Modified client for Roxbot"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	@staticmethod
	def blacklisted(user):
		"""Checks if given user is blacklisted from the bot.
		Params
		=======
		user: discord.User

		Returns
		=======
		If the user is blacklisted: bool"""
		with open("roxbot/settings/blacklist.txt", "r") as fp:
			for line in fp.readlines():
				if str(user.id) + "\n" == line:
					return True
		return False

	async def delete_option(self, message, delete_emoji=None, timeout=20):
		"""Utility function that allows for you to add a delete option to the end of a command.
		This makes it easier for users to control the output of commands, esp handy for random output ones.

		Params
		=======
		message: discord.Message
			Output message from Roxbot
		delete_emoji: discord.Emoji or str if unicode emoji
			Used as the reaction for the user to click on.
		timeout: int (Optional)
			Amount of time in seconds for the bot to wait for the reaction. Deletes itself after the timer runes out.
			Set to 20 by default
		"""
		if not delete_emoji:
			delete_emoji = "❌"
		await message.add_reaction(delete_emoji)

		def check(r, u):
			return str(r) == str(delete_emoji) and u == message.author and r.message.id == message.id

		try:
			await self.wait_for("reaction_add", timeout=timeout, check=check)
			await message.remove_reaction(delete_emoji, self.user)
			try:
				await message.remove_reaction(delete_emoji, message.author)
			except discord.Forbidden:
				pass
			await message.edit(content="{} requested output be deleted.".format(message.author), embed=None)
		except asyncio.TimeoutError:
			await message.remove_reaction(delete_emoji, self.user)

	async def log(self, guild, command_name, **kwargs):
		"""Logs activity internally for Roxbot. Will only do anything if the server enables internal logging.

		This is mostly used for logging when certain commands are used that can be an issue for admins. Esp when Roxbot outputs
		something that could break the rules, then deletes their message.

		Params
		=======
		guild: discord.Guild
			Used to check if the guild has logging enabled
		channel: discord.TextChannel
		command_name: str
		kwargs: dict
			All kwargs and two other params will be added to the logging embed as fields, allowing you to customise the output

		"""
		if guild:
			logging = roxbot.guild_settings.get(guild)["logging"]
			channel = discord.utils.get(guild.channels, id=logging["channel"])
			if logging["enabled"]:
				embed = discord.Embed(title="{} command logging".format(command_name), colour=roxbot.EmbedColours.pink)
				for key, value in kwargs.items():
					embed.add_field(name=key, value=value)
				return await channel.send(embed=embed)



class ErrorHandling:

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

	@staticmethod
	def command_not_found_check(ctx, error):
		try:
			# Sadly this is the only part that makes a cog not modular. I have tried my best though to make it usable without the cog.
			cc = roxbot.guild_settings.get(ctx.guild)["custom_commands"]
			is_custom_command = bool(ctx.invoked_with in cc["1"] or ctx.invoked_with in cc["2"])
			is_emoticon_face = bool(any(x in string.punctuation for x in ctx.message.content.strip(ctx.prefix)[0]))
			is_too_short = bool(len(ctx.message.content) <= 2)
			if is_custom_command or is_emoticon_face or is_too_short:
				return None
			else:
				return error.args[0]
		except (KeyError, AttributeError):
			# KeyError for cog missing, AttributeError if a command invoked via DM
			return error.args[0]

	def command_cooldown_output(self, error):
		try:
			return self.COMMANDONCOOLDOWN.format(error.retry_after)
		except AttributeError:
			return ""

	async def on_command_error(self, ctx, error):
		if self.dev:
			raise error
		else:
			user_error_cases = {
				commands.MissingRequiredArgument: error.args[0],
				commands.BadArgument: error.args[0],
				commands.TooManyArguments: self.TOOMANYARGS,
				roxbot.UserError: error.args[0],
			}
			cases = {
				commands.NoPrivateMessage: self.NODMS,
				commands.DisabledCommand: self.DISABLEDCOMMAND,
				roxbot.CogSettingDisabled: self.COGSETTINGDISABLED.format(error.args[0]),
				commands.CommandNotFound: self.command_not_found_check(ctx, error),
				commands.BotMissingPermissions: "{}".format(error.args[0].replace("Bot", "Roxbot")),
				commands.MissingPermissions: "{}".format(error.args[0]),
				commands.CommandOnCooldown: self.command_cooldown_output(error),
				commands.CheckFailure: self.CHECKFAILURE,
				commands.NotOwner: self.CHECKFAILURE,
			}
			user_error_case = user_error_cases.get(type(error), None)
			case = cases.get(type(error), None)

			# ActualErrorHandling
			embed = discord.Embed(colour=roxbot.EmbedColours.red)
			if case:
				embed.description = case
			elif user_error_case:
				embed.description = user_error_case
				embed.colour = roxbot.EmbedColours.orange
			elif isinstance(error, commands.CommandInvokeError):
				# YOUTUBE_DL ERROR HANDLING
				if isinstance(error.original, youtube_dl.utils.GeoRestrictedError):
					embed.description = self.YTDLDOWNLOADERROR.format("Video is GeoRestricted.")
				elif isinstance(error.original, youtube_dl.utils.DownloadError):
					embed.description = self.YTDLDOWNLOADERROR.format(error.original.exc_info[1])

				# Final catches for errors undocumented.
				else:
					roxbot.logger.error(str(error))
					embed = discord.Embed(title='Command Error', colour=roxbot.EmbedColours.dark_red)
					embed.description = str(error)
					embed.add_field(name='User', value=ctx.author)
					embed.add_field(name='Message', value=ctx.message.content)
					embed.timestamp = datetime.datetime.utcnow()
			elif isinstance(error, commands.CommandError):
				embed.description = "Error: {}".format(error.args[0])
				roxbot.logger.error(embed.description)
			else:
				roxbot.logger.error(str(error))

			if embed:
				embed.colour = roxbot.EmbedColours.dark_red
				await ctx.send(embed=embed)


class Core(ErrorHandling):
	"""Core bot cog. Includes management commands, logging, error handling, and backups."""
	def __init__(self, bot_client):
		self.bot = bot_client
		super().__init__(self.bot)

		# Backup setup
		if roxbot.backup_enabled:
			self.backup_task = self.bot.loop.create_task(self.auto_backups())

		# Logging Setup
		self.bot.add_listener(self.cleanup_logging_settings, "on_guild_channel_delete")
		self.bot.add_listener(self.log_member_join, "on_member_join")
		self.bot.add_listener(self.log_member_remove, "on_member_remove")

		self.settings = {
			"logging": {
				"enabled": 0,
				"convert": {"enabled": "bool", "channel": "channel"},
				"channel": 0
			}
		}

	#############
	#  Logging  #
	#############

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
			embed.add_field(name="Date Account Created", value=roxbot.datetime.format(member.created_at))
			embed.add_field(name="Date Joined", value=roxbot.datetime.format(member.joined_at))
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
		"""Creates a backup of all server's settings manually. This will make a folder in `settings/backups/`.

		The name of the folder will be outputted when you use the command.

		Using only this and not the automatic backups is not recommend.
		"""
		time = datetime.datetime.now()
		filename = "{:%Y.%m.%d %H:%M:%S} Manual Backup".format(time)
		roxbot.guild_settings.backup(filename)
		return await ctx.send("Settings file backed up as a folder named '{}".format(filename))

	############################
	#  Bot Managment Commands  #
	############################

	@commands.command()
	@commands.is_owner()
	async def blacklist(self, ctx, option, users: commands.Greedy[discord.User]):
		""" Manage the global blacklist for Roxbot.

		Options:
			- `option` - This is whether to add or subtract users from the blacklist. `+` or `add` for add and `-` or `remove` for remove.
			- `users` - A name, ID, or mention of a user. This allows multiple users to be mentioned.

		Examples:
			# Add three users to the blacklist
			;blacklist add @ProblemUser1 ProblemUser2#4742 1239274620373
			# Remove one user from the blacklist
			;blacklist - @GoodUser
		"""
		blacklist_amount = 0

		if option not in ['+', '-', 'add', 'remove']:
			raise commands.BadArgument("Invalid option.")

		for user in users:
			if user.id == roxbot.owner:
				await ctx.send("The owner cannot be blacklisted.")
				users.remove(user)

		if option in ['+', 'add']:
			with open("roxbot/settings/blacklist.txt", "r") as fp:
				for user in users:
					for line in fp.readlines():
						if user.id + "\n" in line:
							users.remove(user)

			with open("roxbot/settings/blacklist.txt", "a+") as fp:
				lines = fp.readlines()
				for user in users:
					if user.id not in lines:
						fp.write("{}\n".format(user.id))
						blacklist_amount += 1
			return await ctx.send('{} user(s) have been added to the blacklist'.format(blacklist_amount))

		elif option in ['-', 'remove']:
			with open("roxbot/settings/blacklist.txt", "r") as fp:
				lines = fp.readlines()
			with open("roxbot/settings/blacklist.txt", "w") as fp:
				for user in users:
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
		Changes the avatar of the bot account. This cannot be a gif due to Discord limitations.

		Options:
			- `image` -  This can either be uploaded as an attachment or linked after the command.

		Example:
			# Change avatar to linked image
			;changeavatar https://i.imgur.com/yhRVl9e.png
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
	@commands.guild_only()
	@commands.bot_has_permissions(change_nickname=True)
	async def changenickname(self, ctx, *, nick=None):
		"""Changes the nickname of Roxbot in the guild this command is executed in. 
		
		Options:
			- `name` - OPTIONAL: If not given, Roxbot's nickname will be reset.

		Example:
			# Make Roxbot's nickname "Best Bot 2k18"
			;nick Best Bot 2k18
			# Reset Roxbot's nickname
			;nick
		"""
		await ctx.guild.me.edit(nick=nick, reason=";nick command invoked.")
		return await ctx.send(":thumbsup:")

	@commands.command(aliases=["activity"])
	@commands.is_owner()
	async def changeactivity(self, ctx, *, game: str):
		"""Changes the activity that Roxbot is doing. This will be added as a game. "none" can be passed to remove an activity from Roxbot.
		
		Options:
			- `text` -  Either text to be added as the "game" or none to remove the activity.

		Examples:
			# Change activity to "with the command line" so that it displays "Playing with the command line"
			;activity "with the command line"
			# Stop displaying any activity
			;activity none
		"""
		if game.lower() == "none":
			game = None
		else:
			game = discord.Game(game)
		await self.bot.change_presence(activity=game)
		return await ctx.send(":ok_hand: Activity set to {}".format(str(game)))

	@commands.command(aliases=["status"])
	@commands.is_owner()
	async def changestatus(self, ctx, status: str):
		"""Changes the status of the bot account.
		
		Options:
			- `status` - There are four different options to choose. `online`, `away`, `dnd` (do not disturb), and `offline`

		Examples:
			# Set Roxbot to offline
			;changestatus offline
			# Set Roxbot to online
			;changestatus online
		"""
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
									new_entries.append(str(converter(entry)))
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
		"""Prints settings for the cogs in this guild. 
		Options:
			- cog - OPTIONAL. If given, this will only show the setting of the cog given. This has to be the name the printsettings command gives.

		Examples:
			# Print the settings for the guild 
			;printsettings
			# print settings just for the Admin cog.
			;printsettings Admin
		"""
		option = option.lower()
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

	@commands.command()
	async def invite(self, ctx):
		"""Returns an invite link to invite the bot to your server."""
		link = discord.utils.oauth_url(self.bot.user.id, discord.Permissions(1983245558))
		return await ctx.send("Invite me to your server! <{}>\n\n Disclaimer: {} requests all permissions it requires to run all commands. Some of these can be disabled but some commands may lose functionality.".format(link, self.bot.user.name))

	@commands.command()
	@commands.is_owner()
	async def echo(self, ctx, channel: discord.TextChannel, *, message: str):
		"""Echos the given string to a given channel.
		
		Example:
			# Post the message "Hello World" to the channel #general
			;echo #general Hello World
		"""
		await channel.send(message)
		return await ctx.send(":point_left:")


def setup(bot_client):
	bot_client.add_cog(Core(bot_client))
