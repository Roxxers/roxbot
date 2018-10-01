# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017-2018 Roxanne Gibson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import os
import asyncio
import datetime

import roxbot

import discord
from discord.ext import commands


class System:
	"""Cog for commands that change the bot account and bot running."""
	def __init__(self, bot_client):
		self.bot = bot_client
		self.backup_task = self.bot.loop.create_task(self.auto_backups())

	async def auto_backups(self):
		await self.bot.wait_until_ready()
		raw_settings = {}
		for guild in self.bot.guilds:
			raw_settings = {**raw_settings, **roxbot.guild_settings._open_config(guild, os.listdir('roxbot/settings/servers/{}'.format(guild.id)))}
		while not self.bot.is_closed():
			current_settings = {}
			for guild in self.bot.guilds:
				current_settings = {**current_settings, **roxbot.guild_settings._open_config(guild, os.listdir('roxbot/settings/servers/{}'.format(guild.id)))}
			if raw_settings != current_settings:
				raw_settings = current_settings
				time = datetime.datetime.now()
				roxbot.guild_settings.backup("{:%Y.%m.%d %H:%M:%S} Auto Backup".format(time))
				await asyncio.sleep(300)


	@commands.command()
	@commands.is_owner()
	async def backup(self, ctx):
		time = datetime.datetime.now()
		filename = "{:%Y.%m.%d %H:%M:%S} Manual Backup".format(time)
		roxbot.guild_settings.backup(filename)
		return await ctx.send("Settings file backed up as a folder named '{}".format(filename))

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
				print("[Commands:Blacklist] The owner cannot be blacklisted.")
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

	def parse_setting(self, ctx, settings_to_copy, raw=False):
		settingcontent = ""
		setting = settings_to_copy.copy()
		convert = setting.get("convert", None)
		if convert is not None and not raw:
			for x in convert.keys():
				if convert[x] == "bool":
					if setting[x] == 0:
						setting[x] = "False"
					else:
						setting[x] = "True"
				elif convert[x] == "channel":
					if isinstance(setting[x], list):
						if len(setting[x]) >= 60:
							setting[x] = "There is too many channels to display."
						else:
							new_channels = []
							for channel in setting[x]:
								try:
									new_channels.append(self.bot.get_channel(channel).mention)
								except AttributeError:
									new_channels.append(channel)
							setting[x] = new_channels
					else:
						try:
							setting[x] = self.bot.get_channel(setting[x]).mention
						except AttributeError:
							pass
				elif convert[x] == "role":
					if isinstance(setting[x], list):
						if len(setting[x]) >= 60:
							setting[x] = "There is too many roles to display."
						else:
							new_roles = []
							for role_id in setting[x]:
								try:
									new_roles.append(discord.utils.get(ctx.guild.roles, id=role_id).name)
								except AttributeError:
									new_roles.append(role_id)
							setting[x] = new_roles
					else:
						try:
							setting[x] = discord.utils.get(ctx.guild.roles, id=setting[x]).name
						except AttributeError:
							pass
				elif convert[x] == "user":
					if isinstance(setting[x], list):
						if len(setting[x]) >= 60:
							setting[x] = "There is too many users to display."
						else:
							new_users = []
							for user_id in setting[x]:

								user = self.bot.get_user(user_id)
								if user is None:
									new_users.append(str(user_id))
								else:
									new_users.append(str(user))
							setting[x] = new_users
					else:
						user = self.bot.get_user(setting[x])
						if user is None:
							setting[x] = str(setting[x])
						else:
							setting[x] = str(user)
				elif convert[x] == "hide":
					setting[x] = "This is hidden. Please use other commands to get this data."
		for x in setting.items():
			if x[0] != "convert":
				settingcontent += str(x).strip("()") + "\n"
		return settingcontent

	@commands.command(aliases=["printsettingsraw"])
	@commands.has_permissions(manage_guild=True)
	async def printsettings(self, ctx, option=None):
		"""OWNER OR ADMIN ONLY: Prints the servers settings file."""
		config = roxbot.guild_settings.get(ctx.guild)
		settings = dict(config.settings.copy())  # Make a copy of settings so we don't change the actual settings.
		paginator = commands.Paginator(prefix="```md")
		paginator.add_line("{} settings for {}.\n".format(self.bot.user.name, ctx.message.guild.name))
		if option in settings:
			raw = bool(ctx.invoked_with == "printsettingsraw")
			settingcontent = self.parse_setting(ctx, settings[option], raw=raw)
			paginator.add_line("**{}**".format(option))
			paginator.add_line(settingcontent)
			for page in paginator.pages:
				await ctx.send(page)
		else:
			for setting in settings:
				raw = bool(ctx.invoked_with == "printsettingsraw")
				settingcontent = self.parse_setting(ctx, settings[setting], raw=raw)
				paginator.add_line("**{}**".format(setting))
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
	bot_client.add_cog(System(bot_client))
