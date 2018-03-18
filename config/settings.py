import os
import sys
import aiohttp
import asyncio

import checks
import load_config
from config.server_config import ServerConfig

import discord
from discord.ext.commands import bot, group, is_owner, bot_has_permissions


class Settings:
	"""
	Settings is a mix of settings and admin stuff for the bot. OWNER OR ADMIN ONLY.
	"""
	def __init__(self, bot_client):
		self.bot = bot_client
		self.con = ServerConfig()
		self.serverconfig = self.con.servers

	def get_channel(self, ctx, channel):
		if ctx.message.channel_mentions:
			return ctx.message.channel_mentions[0]
		else:
			return self.bot.get_channel(channel)

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
			with open("config/blacklist.txt", "r") as fp:
				for user in mentions:
					for line in fp.readlines():
						if user.id + "\n" in line:
							mentions.remove(user)

			with open("config/blacklist.txt", "a+") as fp:
				lines = fp.readlines()
				for user in mentions:
					if user.id not in lines:
						fp.write("{}\n".format(user.id))
						blacklist_amount += 1
			return await ctx.send('{} user(s) have been added to the blacklist'.format(blacklist_amount))

		elif option in ['-', 'remove']:
			with open("config/blacklist.txt", "r") as fp:
				lines = fp.readlines()
			with open("config/blacklist.txt", "w") as fp:
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
	async def changenickname(self, ctx, *, nick):
		"""Changes the bot's nickname in the guild.
		Usage:
			;nickname [nickname]"""
		await self.bot.change_nickname(ctx.message.server.me, nick)
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
	async def restart(self):
		"""Restarts the bot."""
		await self.bot.logout()
		return os.execl(sys.executable, sys.executable, *sys.argv)

	@bot.command()
	@is_owner()
	async def shutdown(self):
		"""Shuts down the bot."""
		await self.bot.logout()
		return exit(0)

	@bot.command()
	@checks.is_owner_or_admin()
	async def printsettings(self, ctx, option=None):
		"OWNER OR ADMIN ONLY: Prints the servers config file."
		self.serverconfig = self.con.load_config()
		config = self.serverconfig[str(ctx.guild.id)]
		em = discord.Embed(colour=0xDEADBF)
		em.set_author(name="{} settings for {}.".format(self.bot.user.name, ctx.message.guild.name), icon_url=self.bot.user.avatar_url)
		if option in config:
			settingcontent = ""
			for x in config[option].items():
				settingcontent += str(x).strip("()") + "\n"
			em.add_field(name=option, value=settingcontent, inline=False)
			return await ctx.send(embed=em)
		else:
			for settings in config:
				if settings != "custom_commands" and settings != "warnings":
					settingcontent = ""
					for x in config[settings].items():
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
		self.serverconfig = self.con.load_config()
		self.guild_id = str(ctx.guild.id)

	@settings.command(aliases=["sa"])
	async def selfassign(self, ctx, selection, *, changes = None):
		"""Edits settings for self assign cog.

		Options:
			enable/disable: Enable/disables the cog.
			addrole/removerole: adds or removes a role that can be self assigned in the server.
		"""
		selection = selection.lower()
		role = discord.utils.find(lambda u: u.name == changes, ctx.message.guild.roles)
		if selection == "enable":
			self.serverconfig[self.guild_id]["self_assign"]["enabled"] = 1
			await ctx.send("'self_assign' was enabled!")
		elif selection == "disable":
			self.serverconfig[self.guild_id]["self_assign"]["enabled"] = 0
			await ctx.send("'self_assign' was disabled :cry:")
		elif selection == "addrole":
			if role.id in self.serverconfig[self.guild_id]["self_assign"]["roles"]:
				return await ctx.send("{} is already a self-assignable role.".format(role.name),
										  delete_after=self.con.delete_after)

			self.serverconfig[self.guild_id]["self_assign"]["roles"].append(role.id)
			await ctx.send('Role "{}" added'.format(str(role)))
		elif selection == "removerole":
			if role.id in self.serverconfig[self.guild_id]["self_assign"]["roles"]:
				self.serverconfig[self.guild_id]["self_assign"]["roles"].remove(role.id)
				self.con.update_config(self.serverconfig)
				await ctx.send('"{}" has been removed from the self-assignable roles.'.format(str(role)))
			else:
				return await ctx.send("That role was not in the list.")
		else:
			return await ctx.send("No valid option given.")
		return self.con.update_config(self.serverconfig)

	@settings.command(aliases=["jl"])
	async def joinleave(self, ctx, selection, *, changes = None):
		"""Edits settings for joinleave cog.

		Options:
			enable/disable: Enable/disables parts of the cog. Needs to specify which part.
				Example:
					;settings joinleave enable greets|goodbyes
			welcomechannel/goodbyeschannel: Sets the channels for either option. Must be a ID or mention.
			custommessage: specifies a custom message for the greet messages.
		"""
		selection = selection.lower()
		if selection == "enable":
			if changes == "greets":
				self.serverconfig[self.guild_id]["greets"]["enabled"] = 1
				await ctx.send("'greets' was enabled!")
			elif changes == "goodbyes":
				self.serverconfig[self.guild_id]["goodbyes"]["enabled"] = 1
				await ctx.send("'goodbyes' was enabled!")
		elif selection == "disable":
			if changes == "greets":
				self.serverconfig[self.guild_id]["greets"]["enabled"] = 0
				await ctx.send("'greets' was disabled :cry:")
			elif changes == "goodbyes":
				self.serverconfig[self.guild_id]["goodbyes"]["enabled"] = 0
				await ctx.send("'goodbyes' was disabled :cry:")
		elif selection == "welcomechannel":
			channel = self.get_channel(ctx, changes)
			self.serverconfig[self.guild_id]["greets"]["welcome-channel"] = channel.id
			await ctx.send("{} has been set as the welcome channel!".format(channel.mention))
		elif selection == "goodbyeschannel":
			channel = self.get_channel(ctx, changes)
			self.serverconfig[self.guild_id]["goodbyes"]["goodbye-channel"] = channel.id
			await ctx.send("{} has been set as the goodbye channel!".format(channel.mention))
		elif selection == "custommessage":
			self.serverconfig[self.guild_id]["greets"]["custom-message"] = changes
			await ctx.send("Custom message set to '{}'".format(changes))
		else:
			return await ctx.send("No valid option given.")
		return self.con.update_config(self.serverconfig)

	@settings.command()
	async def twitch(self, ctx, selection, *, changes = None):
		"""Edits settings for self assign cog.

		Options:
			enable/disable: Enable/disables the cog.
			channel: Sets the channel to shill in.
		"""
		selection = selection.lower()
		if selection == "enable":
			self.serverconfig[self.guild_id]["twitch"]["enabled"] = 1
			await ctx.send("'twitch' was enabled!")
		elif selection == "disable":
			self.serverconfig[self.guild_id]["twitch"]["enabled"] = 0
			await ctx.send("'twitch' was disabled :cry:")
		elif selection == "channel":
			channel = self.get_channel(ctx, changes)
			self.serverconfig[self.guild_id]["twitch"]["channel"] = channel.id
			await ctx.send("{} has been set as the twitch shilling channel!".format(channel.mention))
		# Is lacking whitelist options. Might be added or might be depreciated.
		# Turns out this is handled in the cog and I don't think it needs changing but may be confusing.
		else:
			return await ctx.send("No valid option given.")
		return self.con.update_config(self.serverconfig)

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
		if selection == "addadmin":
			if role.id not in self.serverconfig[self.guild_id]["perm_roles"]["admin"]:
				self.serverconfig[self.guild_id]["perm_roles"]["admin"].append(role.id)
				await ctx.send("'{}' has been added to the Admin role list.".format(role.name))
			else:
				return await ctx.send("'{}' is already in the list.".format(role.name))
		elif selection == "addmod":
			if role.id not in self.serverconfig[self.guild_id]["perm_roles"]["mod"]:
				self.serverconfig[self.guild_id]["perm_roles"]["mod"].append(role.id)
				await ctx.send("'{}' has been added to the Mod role list.".format(role.name))
			else:
				return await ctx.send("'{}' is already in the list.".format(role.name))
		elif selection == "removeadmin":
			try:
				self.serverconfig[self.guild_id]["perm_roles"]["admin"].remove(role.id)
				await ctx.send("'{}' has been removed from the Admin role list.".format(role.name))
			except ValueError:
				return await ctx.send("That role was not in the list.")
		elif selection == "removemod":
			try:
				self.serverconfig[self.guild_id]["perm_roles"]["mod"].remove(role.id)
				await ctx.send("'{}' has been removed from the Mod role list.".format(role.name))
			except ValueError:
				return await ctx.send("That role was not in the list.")

		else:
			return await ctx.send("No valid option given.")
		return self.con.update_config(self.serverconfig)

	@settings.command()
	async def gss(self, ctx, selection, *, changes = None):
		"""Custom Cog for the GaySoundsShitposts Discord Server."""
		selection = selection.lower()
		if selection == "loggingchannel":
			channel = self.get_channel(ctx, changes)
			self.serverconfig[self.guild_id]["gss"]["log_channel"] = channel.id
			await ctx.send("Logging Channel set to '{}'".format(channel.name))
		elif selection == "requireddays":
			self.serverconfig[self.guild_id]["gss"]["required_days"] = int(changes)
			await ctx.send("Required days set to '{}'".format(str(changes)))
		elif selection == "requiredscore":
			self.serverconfig[self.guild_id]["gss"]["required_score"] = int(changes)
			await ctx.send("Required score set to '{}'".format(str(changes)))
		else:
			return await ctx.send("No valid option given.")
		return self.con.update_config(self.serverconfig)


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
		if selection == "enable":
			self.serverconfig[self.guild_id]["nsfw"]["enabled"] = 1
			await ctx.send("'nsfw' was enabled!")
		elif selection == "disable":
			self.serverconfig[self.guild_id]["nsfw"]["enabled"] = 0
			await ctx.send("'nsfw' was disabled :cry:")
		elif selection == "addchannel":
			channel = self.get_channel(ctx, changes)
			if channel.id not in self.serverconfig[self.guild_id]["nsfw"]["channels"]:
				self.serverconfig[self.guild_id]["nsfw"]["channels"].append(channel.id)
				await ctx.send("'{}' has been added to the nsfw channel list.".format(channel.name))
			else:
				return await ctx.send("'{}' is already in the list.".format(channel.name))
		elif selection == "removechannel":
			channel = self.get_channel(ctx, changes)
			try:
				self.serverconfig[self.guild_id]["nsfw"]["channels"].remove(channel.id)
				await ctx.send("'{}' has been removed from the nsfw channel list.".format(channel.name))
			except ValueError:
				return await ctx.send("That role was not in the list.")
		elif selection == "addbadtag":
			if changes not in self.serverconfig[self.guild_id]["nsfw"]["blacklist"]:
				self.serverconfig[self.guild_id]["nsfw"]["blacklist"].append(changes)
				await ctx.send("'{}' has been added to the blacklisted tag list.".format(changes))
			else:
				return await ctx.send("'{}' is already in the list.".format(changes))
		elif selection == "removebadtag":
			try:
				self.serverconfig[self.guild_id]["nsfw"]["blacklist"].remove(changes)
				await ctx.send("'{}' has been removed from the blacklisted tag list.".format(changes))
			except ValueError:
				return await ctx.send("That tag was not in the blacklisted tag list.")
		else:
			return await ctx.send("No valid option given.")
		return self.con.update_config(self.serverconfig)

	@checks.is_admin_or_mod()
	@bot.command()
	async def serverisanal(self, ctx):
		"""Tells the bot where the server is anal or not.
		This only changes if roxbot can do the suck and spank commands outside of the specified nsfw channels."""
		self.serverconfig = self.con.load_config()
		is_anal = self.serverconfig[self.guild_id]["is_anal"]["y/n"]
		if is_anal == 0:
			self.serverconfig[self.guild_id]["is_anal"]["y/n"] = 1
			self.con.update_config(self.serverconfig)
			return await ctx.send("I now know this server is anal")
		else:
			self.serverconfig[self.guild_id]["is_anal"]["y/n"] = 0
			self.con.update_config(self.serverconfig)
			return await ctx.send("I now know this server is NOT anal")


def setup(bot_client):
	bot_client.add_cog(Settings(bot_client))