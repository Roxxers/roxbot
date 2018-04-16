import os
import sys
import aiohttp
import asyncio
import datetime

from Roxbot import checks, load_config
from Roxbot.settings import guild_settings

import discord
from discord.ext.commands import bot, group, is_owner, bot_has_permissions


class Settings:
	"""
	Settings is a mix of settings and admin stuff for the bot. OWNER OR ADMIN ONLY.
	"""
	def __init__(self, bot_client):
		self.bot = bot_client
		self.bg_task = self.bot.loop.create_task(self.auto_backups())

	def get_channel(self, ctx, channel):
		if ctx.message.channel_mentions:
			return ctx.message.channel_mentions[0]
		else:
			return self.bot.get_channel(channel)

	async def auto_backups(self):
		await self.bot.wait_until_ready()
		raw_settings = guild_settings._open_config()
		while not self.bot.is_closed():
			if raw_settings != guild_settings._open_config():
				raw_settings = guild_settings._open_config()
				time = datetime.datetime.now()
				guild_settings.backup(raw_settings, "{:%Y.%m.%d %H:%M:%S} Auto Backup".format(time))
			await asyncio.sleep(300)

	@bot.command()
	@is_owner()
	async def backup(self, ctx):
		time = datetime.datetime.now()
		filename = "{:%Y.%m.%d %H:%M:%S} Manual Backup".format(time)
		guild_settings.backup(guild_settings._open_config(), filename)
		return await ctx.send("Settings file backed up as '{}.json'".format(filename))

	@bot.command()
	@checks.is_owner_or_admin()
	async def blacklist(self, ctx, option):
		"""
		Add or remove users to the blacklist. Blacklisted users are forbidden from using bot commands.
		Usage:
			;blacklist [add|+ OR remove|-] @user#0000
		OWNER OR ADMIN ONLY
		"""
		blacklist_amount = 0
		mentions = ctx.message.mentions

		if not mentions:
			return await ctx.send("You didn't mention anyone")

		if option not in ['+', '-', 'add', 'remove']:
			return await ctx.send('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

		for user in mentions:
			if user.id == load_config.owner:
				print("[Commands:Blacklist] The owner cannot be blacklisted.")
				await ctx.send("The owner cannot be blacklisted.")
				mentions.remove(user)

		if option in ['+', 'add']:
			with open("settings/blacklist.txt", "r") as fp:
				for user in mentions:
					for line in fp.readlines():
						if user.id + "\n" in line:
							mentions.remove(user)

			with open("settings/blacklist.txt", "a+") as fp:
				lines = fp.readlines()
				for user in mentions:
					if user.id not in lines:
						fp.write("{}\n".format(user.id))
						blacklist_amount += 1
			return await ctx.send('{} user(s) have been added to the blacklist'.format(blacklist_amount))

		elif option in ['-', 'remove']:
			with open("settings/blacklist.txt", "r") as fp:
				lines = fp.readlines()
			with open("settings/blacklist.txt", "w") as fp:
				for user in mentions:
					for line in lines:
						if user.id + "\n" != line:
							fp.write(line)
						else:
							fp.write("")
							blacklist_amount += 1
				return await ctx.send('{} user(s) have been removed from the blacklist'.format(blacklist_amount))

	@bot.command(aliases=["setavatar"])
	@is_owner()
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
			thing = url.strip('<>')

			async with aiohttp.ClientSession() as session:
				async with session.get(thing) as img:
					with open(avaimg, 'wb') as f:
						f.write(await img.read())
		with open(avaimg, 'rb') as f:
			await self.bot.user.edit(avatar=f.read())
		os.remove(avaimg)
		asyncio.sleep(2)
		return await ctx.send(":ok_hand:")

	@bot.command(aliases=["nick", "nickname"])
	@is_owner()
	@bot_has_permissions(change_nickname=True)
	async def changenickname(self, ctx, *, nick = None):
		"""Changes the bot's nickname in the guild.
		Usage:
			;nickname [nickname]"""
		await ctx.guild.me.edit(nick=nick, reason=";nick command invoked.")
		return await ctx.send(":thumbsup:")

	@bot.command(aliases=["activity"])
	@is_owner()
	async def changeactivity(self, ctx, *, game: str):
		"""Changes the "playing" status of the bot.
		Usage:
			;changeactivity` [game]"""
		if game.lower() == "none":
			game= None
		else:
			game = discord.Game(game)
		await self.bot.change_presence(activity=game)
		return await ctx.send(":ok_hand: Activity set to {}".format(str(game)))

	@bot.command(aliases=["status"])
	@is_owner()
	async def changestatus(self, ctx, status: str):
		"""Changes the status of the bot.
		Usage:
			;changesatus [game]"""
		status = status.lower()
		if status == 'offline' or status == 'invisible':
			discordStatus = discord.Status.invisible
		elif status == 'idle':
			discordStatus = discord.Status.idle
		elif status == 'dnd':
			discordStatus = discord.Status.dnd
		else:
			discordStatus = discord.Status.online
		await self.bot.change_presence(status=discordStatus)
		await ctx.send("**:ok:** Status set to {}".format(discordStatus))

	@bot.command()
	@is_owner()
	async def restart(self, ctx):
		"""Restarts the bot."""
		await self.bot.logout()
		return os.execl(sys.executable, sys.executable, *sys.argv)

	@bot.command()
	@is_owner()
	async def shutdown(self, ctx):
		"""Shuts down the bot."""
		await self.bot.logout()
		return exit(0)

	@bot.command()
	@checks.is_owner_or_admin()
	async def printsettings(self, ctx, option=None):
		"OWNER OR ADMIN ONLY: Prints the servers settings file."
		config = guild_settings.get(ctx.guild)
		em = discord.Embed(colour=0xDEADBF)
		em.set_author(name="{} settings for {}.".format(self.bot.user.name, ctx.message.guild.name), icon_url=self.bot.user.avatar_url)
		if option in config.settings:
			settingcontent = ""
			for x in config.settings[option].items():
				settingcontent += str(x).strip("()") + "\n"
			em.add_field(name=option, value=settingcontent, inline=False)
			return await ctx.send(embed=em)
		else:
			for settings in config.settings:
				if settings != "custom_commands" and settings != "warnings":
					settingcontent = ""
					for x in config.settings[settings].items():
						settingcontent += str(x).strip("()") + "\n"
					em.add_field(name=settings, value=settingcontent, inline=False)
				elif settings == "custom_commands":
					em.add_field(name="custom_commands", value="For Custom Commands, use the custom list command.", inline=False)
			return await ctx.send(embed=em)

	@group()
	@checks.is_admin_or_mod()
	async def settings(self, ctx):
		if ctx.invoked_subcommand is None:
			return await ctx.send('Missing Argument')
		self.guild_settings = guild_settings.get(ctx.guild)

	@settings.command(aliases=["log"])
	async def logging(self, ctx, selection, *, changes = None):
		"""Edits the logging settings.

		Options:
			enable/disable: Enable/disables logging.
			channel: sets the channel.
		"""
		selection = selection.lower()
		settings = guild_settings.get(ctx.guild)

		if selection == "enable":
			settings.logging["enabled"] = 1
			await ctx.send("'logging' was enabled!")
		elif selection == "disable":
			settings.logging["enabled"] = 0
			await ctx.send("'logging' was disabled :cry:")
		elif selection == "channel":
			channel = self.get_channel(ctx, changes)
			settings.logging["channel"] = channel.id
			await ctx.send("{} has been set as the logging channel!".format(channel.mention))
		else:
			return await ctx.send("No valid option given.")
		return self.guild_settings.update(settings.logging, "logging")


	@settings.command(aliases=["sa"])
	async def selfassign(self, ctx, selection, *, changes = None):
		"""Edits settings for self assign cog.

		Options:
			enable/disable: Enable/disables the cog.
			addrole/removerole: adds or removes a role that can be self assigned in the server.
		"""
		selection = selection.lower()
		role = discord.utils.find(lambda u: u.name == changes, ctx.message.guild.roles)
		self_assign = self.guild_settings.self_assign

		if selection == "enable":
			self_assign["enabled"] = 1
			await ctx.send("'self_assign' was enabled!")
		elif selection == "disable":
			self_assign["enabled"] = 0
			await ctx.send("'self_assign' was disabled :cry:")
		elif selection == "addrole":
			if role.id in self_assign["roles"]:
				return await ctx.send("{} is already a self-assignable role.".format(role.name))
			self_assign["roles"].append(role.id)
			await ctx.send('Role "{}" added'.format(str(role)))
		elif selection == "removerole":
			if role.id in self_assign["roles"]:
				self_assign["roles"].remove(role.id)
				await ctx.send('"{}" has been removed from the self-assignable roles.'.format(str(role)))
			else:
				return await ctx.send("That role was not in the list.")
		else:
			return await ctx.send("No valid option given.")
		return self.guild_settings.update(self_assign, "self_assign")

	@settings.command(aliases=["jl"])
	async def joinleave(self, ctx, selection, *, changes = None):
		"""Edits settings for joinleave cog.

		Options:
			enable/disable: Enable/disables parts of the cog. Needs to specify which part.
				Example:
					;settings joinleave enable greets|goodbyes
			greetschannel/goodbyeschannel: Sets the channels for either option. Must be a ID or mention.
			custommessage: specifies a custom message for the greet messages.
		"""
		selection = selection.lower()
		channel = self.get_channel(ctx, changes)
		greets = self.guild_settings.greets
		goodbyes = self.guild_settings.goodbyes

		if changes == "greets":
			if selection == "enable":
				greets["enabled"] = 1
				await ctx.send("'greets' was enabled!")
			elif selection == "disable":
				greets["enabled"] = 0
				await ctx.send("'greets' was disabled :cry:")

		elif changes == "goodbyes":
			if selection == "enable":
				goodbyes["enabled"] = 1
				await ctx.send("'goodbyes' was enabled!")
			elif selection == "disable":
				goodbyes["enabled"] = 0
				await ctx.send("'goodbyes' was disabled :cry:")

		else:
			if selection == "greetschannel":
				greets["welcome-channel"] = channel.id
				changes = "greets"
				await ctx.send("{} has been set as the welcome channel!".format(channel.mention))
			elif selection == "goodbyeschannel":
				goodbyes["goodbye-channel"] = channel.id
				changes = "goodbyes"
				await ctx.send("{} has been set as the goodbye channel!".format(channel.mention))
			elif selection == "custommessage":
				greets["custom-message"] = changes
				await ctx.send("Custom message set to '{}'".format(changes))
				changes = "greets"
			else:
				return await ctx.send("No valid option given.")

		if changes == "greets":
			return self.guild_settings.update(greets, "greets")
		elif changes == "goodbyes":
			return self.guild_settings.update(goodbyes, "goodbyes")

	@settings.command()
	async def twitch(self, ctx, selection, *, changes = None):
		"""Edits settings for self assign cog.

		Options:
			enable/disable: Enable/disables the cog.
			channel: Sets the channel to shill in.
		"""
		selection = selection.lower()
		twitch = self.guild_settings.twitch

		if selection == "enable":
			twitch["enabled"] = 1
			await ctx.send("'twitch' was enabled!")
		elif selection == "disable":
			twitch["enabled"] = 0
			await ctx.send("'twitch' was disabled :cry:")
		elif selection == "channel":
			channel = self.get_channel(ctx, changes)
			twitch["channel"] = channel.id
			await ctx.send("{} has been set as the twitch shilling channel!".format(channel.mention))
		# Is lacking whitelist options. Might be added or might be depreciated.
		# Turns out this is handled in the cog and I don't think it needs changing but may be confusing.
		else:
			return await ctx.send("No valid option given.")
		return self.guild_settings.update(twitch, "twitch")

	@settings.command(aliases=["perms"])
	async def permrole(self, ctx, selection, *, changes = None):
		"""Edits settings for permission roles.

		Options:
			addadmin/removeadmin: Adds/Removes admin role.
			addmod/removemod: Adds/Removes mod role.
		Example:
			;settings permrole addadmin Admin
		"""
		selection = selection.lower()
		role = discord.utils.find(lambda u: u.name == changes, ctx.message.guild.roles)
		perm_roles = self.guild_settings.perm_roles

		if selection == "addadmin":
			if role.id not in perm_roles["admin"]:
				perm_roles["admin"].append(role.id)
				await ctx.send("'{}' has been added to the Admin role list.".format(role.name))
			else:
				return await ctx.send("'{}' is already in the list.".format(role.name))
		elif selection == "addmod":
			if role.id not in perm_roles["mod"]:
				perm_roles["mod"].append(role.id)
				await ctx.send("'{}' has been added to the Mod role list.".format(role.name))
			else:
				return await ctx.send("'{}' is already in the list.".format(role.name))
		elif selection == "removeadmin":
			try:
				perm_roles["admin"].remove(role.id)
				await ctx.send("'{}' has been removed from the Admin role list.".format(role.name))
			except ValueError:
				return await ctx.send("That role was not in the list.")
		elif selection == "removemod":
			try:
				perm_roles["mod"].remove(role.id)
				await ctx.send("'{}' has been removed from the Mod role list.".format(role.name))
			except ValueError:
				return await ctx.send("That role was not in the list.")

		else:
			return await ctx.send("No valid option given.")
		return self.guild_settings.update(perm_roles, "perm_roles")

	@settings.command()
	async def gss(self, ctx, selection, *, changes = None):
		"""Custom Cog for the GaySoundsShitposts Discord Server."""
		selection = selection.lower()
		gss = self.guild_settings.gss

		if selection == "loggingchannel":
			channel = self.get_channel(ctx, changes)
			gss["log_channel"] = channel.id
			await ctx.send("Logging Channel set to '{}'".format(channel.name))
		elif selection == "requireddays":
			gss["required_days"] = int(changes)
			await ctx.send("Required days set to '{}'".format(str(changes)))
		elif selection == "requiredscore":
			gss["required_score"] = int(changes)
			await ctx.send("Required score set to '{}'".format(str(changes)))
		else:
			return await ctx.send("No valid option given.")
		return self.guild_settings.update(gss, "gss")


	@settings.command()
	async def nsfw(self, ctx, selection, *, changes = None):
		"""Edits settings for the nsfw cog and other nsfw commands.
		If nsfw is enabled and nsfw channels are added, the bot will only allow nsfw commands in the specified channels.

		Options:
			enable/disable: Enable/disables nsfw commands.
			addchannel/removechannel: Adds/Removes a nsfw channel.
			Example:
				;settings nsfw addchannel #nsfw_stuff
		"""
		selection = selection.lower()
		nsfw = self.guild_settings.nsfw

		if selection == "enable":
			nsfw["enabled"] = 1
			await ctx.send("'nsfw' was enabled!")
		elif selection == "disable":
			nsfw["enabled"] = 0
			await ctx.send("'nsfw' was disabled :cry:")
		elif selection == "addchannel":
			channel = self.get_channel(ctx, changes)
			if channel.id not in nsfw["channels"]:
				nsfw["channels"].append(channel.id)
				await ctx.send("'{}' has been added to the nsfw channel list.".format(channel.name))
			else:
				return await ctx.send("'{}' is already in the list.".format(channel.name))
		elif selection == "removechannel":
			channel = self.get_channel(ctx, changes)
			try:
				nsfw["channels"].remove(channel.id)
				await ctx.send("'{}' has been removed from the nsfw channel list.".format(channel.name))
			except ValueError:
				return await ctx.send("That role was not in the list.")
		elif selection == "addbadtag":
			if changes not in nsfw["nsfw"]["blacklist"]:
				nsfw["blacklist"].append(changes)
				await ctx.send("'{}' has been added to the blacklisted tag list.".format(changes))
			else:
				return await ctx.send("'{}' is already in the list.".format(changes))
		elif selection == "removebadtag":
			try:
				nsfw["blacklist"].remove(changes)
				await ctx.send("'{}' has been removed from the blacklisted tag list.".format(changes))
			except ValueError:
				return await ctx.send("That tag was not in the blacklisted tag list.")
		else:
			return await ctx.send("No valid option given.")
		return self.guild_settings.update(nsfw, "nsfw")

	@settings.command()
	async def voice(self, ctx, setting, change):
		"""Edits settings for the voice cog.
		Options:
			enable/disable: Enable/disables specified change.
			skipratio: Specify what the ratio should be for skip voting if enabled. Example: 0.6 for 60%
			maxlength: Specify (in seconds) the max duration of a video that can be played. Ignored if staff of the server/bot owner.
		Possible settings to enable/disable:
			needperms: specifies whether volume controls and other bot functions need mod/admin perms.
			skipvoting: specifies whether skipping should need over half of voice users to vote to skip. Bypassed by mods.
		Example:
			;settings voice enable skipvoting
		"""
		setting = setting.lower()
		change = change.lower()
		voice = self.guild_settings.voice

		if setting == "enable":
			if change == "needperms":
				voice["need_perms"] = 1
				await ctx.send("'{}' has been enabled!".format(change))
			elif change == "skipvoting":
				voice["skip_voting"] = 1
				await ctx.send("'{}' has been enabled!".format(change))
			else:
				return await ctx.send("Not a valid change.")
		elif setting == "disable":
			if change == "needperms":
				voice["need_perms"] = 1
				await ctx.send("'{}' was disabled :cry:".format(change))
			elif change == "skipvoting":
				voice["skip_voting"] = 1
				await ctx.send("'{}' was disabled :cry:".format(change))
			else:
				return await ctx.send("Not a valid change.")
		elif setting == "skipratio":
			if isinstance(change, int):
				if change < 1 and change > 0:
					voice["skip_ratio"] = change
				elif change > 0 and change <= 100:
					change = change/10
					voice["skip_ratio"] = change
				else:
					return await ctx.send("Valid ratio not given.")
			else:
				return await ctx.send("Valid ratio not given.")
			await ctx.send("Skip Ratio was set to {}".format(change))
		elif setting == "maxlength":
			if isinstance(change, int):
				if change >= 1:
					voice["skip_ratio"] = change
				else:
					return await ctx.send("Valid max duration not given.")
			else:
				return await ctx.send("Valid max duration not given.")
			await ctx.send("Skip Ratio was set to {}".format(change))
		else:
			return await ctx.send("Valid option not given.")
		return self.guild_settings.update(voice, "voice")

	@checks.is_admin_or_mod()
	@bot.command()
	async def serverisanal(self, ctx):
		"""Tells the bot where the server is anal or not.
		This only changes if roxbot can do the suck and spank commands outside of the specified nsfw channels."""
		is_anal = self.guild_settings.is_anal
		if is_anal["y/n"] == 0:
			is_anal["y/n"] = 1
			self.guild_settings.update(is_anal, "is_anal")
			await ctx.send("I now know this server is anal")
		else:
			is_anal["y/n"] = 0
			self.guild_settings.update(is_anal, "is_anal")
			await ctx.send("I now know this server is NOT anal")
		return self.guild_settings.update()


def setup(bot_client):
	bot_client.add_cog(Settings(bot_client))