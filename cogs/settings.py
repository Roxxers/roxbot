import os
import sys
import aiohttp
import asyncio

import checks
import load_config
from config.server_config import ServerConfig

import discord
from discord.ext.commands import bot
from discord.ext.commands import group


class Settings():
	"""
	Settings is a mix of settings and admin stuff for the bot. OWNER OR ADMIN ONLY.
	"""
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	@bot.command(pass_context=True)
	@checks.is_owner_or_admin()
	async def blacklist(self, ctx, option, *args):
		"""
		OWNER OR ADMIN ONLY: Add or remove users to the blacklist.
		Blacklisted users are forbidden from using bot commands.
		"""
		blacklist_amount = 0
		mentions = ctx.message.mentions

		if not mentions:
			return await self.bot.say("You didn't mention anyone")

		if option not in ['+', '-', 'add', 'remove']:
			return await self.bot.say('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

		for user in mentions:
			if user.id == load_config.owner:
				print("[Commands:Blacklist] The owner cannot be blacklisted.")
				await self.bot.say("The owner cannot be blacklisted.")
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
			return await self.bot.say('{} user(s) have been added to the blacklist'.format(blacklist_amount))

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
				return await self.bot.say('{} user(s) have been removed from the blacklist'.format(blacklist_amount))

	@bot.command(pass_context=True, hidden=True, aliases=["setava", "setavatar"])
	@checks.is_bot_owner()
	async def changeavatar(self, ctx, url=None):
		"""
		Usage:
			{command_prefix}setavatar [url]
		Changes the bot's avatar.
		Attaching a file and leaving the url parameter blank also works.
		"""
		if ctx.message.attachments:
			thing = ctx.message.attachments[0]['url']
		else:
			thing = url.strip('<>')

		avaimg = 'avaimg'
		async with aiohttp.ClientSession() as session:
			async with session.get(thing) as img:
				with open(avaimg, 'wb') as f:
					f.write(await img.read())
		with open(avaimg, 'rb') as f:
			await self.bot.edit_profile(avatar=f.read())
		os.remove(avaimg)
		asyncio.sleep(2)
		return await self.bot.say(":ok_hand:")

	@bot.command(pass_context=True, hidden=True, aliases=["nick"])
	@checks.is_bot_owner()
	async def changenickname(self, ctx, *nick):
		if ctx.message.channel.permissions_for(ctx.message.server.me).change_nickname:
			await self.bot.change_nickname(ctx.message.server.me, ' '.join(nick))
			return await self.bot.say(":thumbsup:")
		else:
			return await self.bot.say("I don't have permission to do that :sob:", delete_after=self.con.delete_after)

	@bot.command(pass_context=True, hidden=True, aliases=["setgame", "game"])
	@checks.is_bot_owner()
	async def changegame(self, ctx, *, game: str):
		if game.lower() == "none":
			game_name = None
		else:
			game_name = discord.Game(name=game, type=0)
		await self.bot.change_presence(game=game_name, afk=False)
		return await self.bot.say(":ok_hand: Game set to {}".format(str(game_name)))

	@bot.command(pass_context=True, hidden=True, aliases=["status"])
	@checks.is_bot_owner()
	async def changestatus(self, ctx, status: str):
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
		await self.bot.say("**:ok:** Status set to {}".format(discordStatus))

	@bot.command(hidden=True)
	@checks.is_bot_owner()
	async def restart(self):
		await self.bot.logout()
		return os.execl(sys.executable, sys.executable, *sys.argv)

	@bot.command(hidden=True)
	@checks.is_bot_owner()
	async def shutdown(self):
		await self.bot.logout()
		return exit(0)

	@bot.command(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def announce(self, ctx, *announcement):
		"""
		ONLY USE FOR SERIOUS ANNOUNCEMENTS
		"""
		# TODO: Make colour top level role colour
		# TODO: Custom message for annoucement footer
		embed = discord.Embed(title="RoxBot Announcement", colour=discord.Colour(0x306f99), description=' '.join(announcement))
		embed.set_footer(text="This message has be automatically generated by a cute ass Roxie",
						 icon_url=self.bot.user.avatar_url)
		for server in self.bot.servers:
			await self.bot.send_message(server, embed=embed)
		return await self.bot.say("Done!", delete_after=self.con.delete_after)

	@bot.command(pass_context=True)
	@checks.is_owner_or_admin()
	async def printsettings(self, ctx):
		"OWNER OR ADMIN ONLY: Prints the servers config file."
		self.serverconfig = self.con.load_config()
		config = self.serverconfig[ctx.message.server.id]
		em = discord.Embed(colour=0xDEADBF)
		em.set_author(name="{} settings for {}.".format(self.bot.user.name, ctx.message.server.name), icon_url=self.bot.user.avatar_url)

		for settings in config:
			if settings != "custom_commands":
				settingcontent = ""
				for x in config[settings].items():
					settingcontent += str(x).strip("()") + "\n"
				em.add_field(name=settings, value=settingcontent, inline=False)
			else:
				em.add_field(name="custom_commands", value="For Custom Commands, use the custom list command.", inline=False)

		return await self.bot.say(embed=em)


	@group(pass_context=True)
	async def settings(self, ctx):
		pass

	@settings.command(pass_context=True)
	async def self_assign(self, ctx, selection, *, changes = None):
		if selection == "enable":
			pass



	@bot.command(pass_context=True)
	@checks.is_owner_or_admin()
	async def enablesetting(self, ctx, setting):
		"OWNER OR ADMIN ONLY: Enables settings in the server config."
		self.serverconfig = self.con.load_config()
		server_id = ctx.message.server.id
		if setting in self.serverconfig[server_id]:
			if not self.serverconfig[server_id][setting]["enabled"]:
				self.serverconfig[server_id][setting]["enabled"] = 1
				self.con.update_config(self.serverconfig)
				return await self.bot.say("'{}' was enabled!".format(setting))
			else:
				self.serverconfig[server_id][setting]["enabled"] = 0
				self.con.update_config(self.serverconfig)
				return await self.bot.say("'{}' was disabled :cry:".format(setting))
		else:
			return await self.bot.say("That module dont exist fam. You made the thing")



	@group(pass_context=True, hidden=True)
	@checks.is_admin_or_mod()
	async def set(self, ctx):
		if ctx.invoked_subcommand is None:
			return await self.bot.say('Missing Argument')

	@set.command(pass_context=True, hidden=True)
	async def welcomechannel(self, ctx, channel: discord.Channel = None):
		self.servers = self.con.load_config()
		self.servers[ctx.message.server.id]["greets"]["welcome-channel"] = channel.id
		self.con.update_config(self.servers)
		return await self.bot.say("{} has been set as the welcome channel!".format(channel.mention))

	@set.command(pass_context=True, hidden=True)
	async def goodbyechannel(self, ctx, channel: discord.Channel = None):
		self.servers = self.con.load_config()
		self.servers[ctx.message.server.id]["goodbyes"]["goodbye-channel"] = channel.id
		self.con.update_config(self.servers)
		return await self.bot.say("{} has been set as the goodbye channel!".format(channel.mention))

	@set.command(pass_context=True, hidden=True)
	async def twitchchannel(self, ctx, channel: discord.Channel = None): # Idk if this should be here, maybe in thw twitch cog?
		self.servers = self.con.load_config()
		self.servers[ctx.message.server.id]["twitch"]["twitch-channel"] = channel.id
		self.con.update_config(self.servers)
		return await self.bot.say("{} has been set as the twitch shilling channel!".format(channel.mention))

	@set.command(pass_context=True, hidden=True)
	async def welcomemessage(self, ctx, *, message: str):
		print(ctx)
		self.servers = self.con.load_config()
		self.servers[ctx.message.server.id]["greets"]["custom-message"] = message
		self.con.update_config(self.servers)
		return await self.bot.say("Custom message set to '{}'".format(message))

	@set.command(pass_context=True, hidden=True)
	async def muterole(self, ctx, role: discord.Role = None):
		self.servers = self.con.load_config()
		self.servers[ctx.message.server.id]["mute"]["role"] = role.id
		self.con.update_config(self.servers)
		return await self.bot.say("Muted role set to '{}'".format(role.name))

	@set.command(pass_context=True, hidden=True)
	async def loggingchannel(self, ctx, channel: discord.Channel = None):
		self.servers = self.con.load_config()
		self.servers[ctx.message.server.id]["gss"]["logging_channel"] = channel.id
		self.con.update_config(self.servers)
		return await self.bot.say("Logging Channel set to '{}'".format(channel.name))

	@set.command(pass_context=True, hidden=True)
	async def requireddays(self, ctx, days: int):
		self.servers = self.con.load_config()
		self.servers[ctx.message.server.id]["gss"]["required_days"] = str(days)
		self.con.update_config(self.servers)
		return await self.bot.say("Required days set to '{}'".format(str(days)))

	@set.command(pass_context=True, hidden=True)
	async def requiredscore(self, ctx, score: int):
		self.servers = self.con.load_config()
		self.servers[ctx.message.server.id]["gss"]["required_score"] = str(score)
		self.con.update_config(self.servers)
		return await self.bot.say("Required score set to '{}'".format(str(score)))

	@group(pass_context=True)
	@checks.is_owner_or_admin()
	async def add(self, ctx):
		"OWNER OR ADMIN ONLY: Adds to lists like admin roles."
		if ctx.invoked_subcommand is None:
			return await self.bot.say('Missing Argument')

	@add.command(pass_context=True, aliases=["adminrole"])
	async def addadminrole(self, ctx, *, role: discord.Role = None):
		self.servers = self.con.load_config()
		if role.id not in self.servers[ctx.message.server.id]["perm_roles"]["admin"]:
			self.servers[ctx.message.server.id]["perm_roles"]["admin"].append(role.id)
			self.con.update_config(self.servers)
			return await self.bot.say("'{}' has been added to the Admin role list.".format(role.name))
		else:
			return await self.bot.say("'{}' is already in the list.".format(role.name))

	@add.command(pass_context=True, aliases=["modrole"])
	async def addmodrole(self, ctx, *, role: discord.Role = None):
		self.servers = self.con.load_config()
		if role.id not in self.servers[ctx.message.server.id]["perm_roles"]["mod"]:
			self.servers[ctx.message.server.id]["perm_roles"]["mod"].append(role.id)
			self.con.update_config(self.servers)
			return await self.bot.say("'{}' has been added to the Mod role list.".format(role.name))
		else:
			return await self.bot.say("'{}' is already in the list.".format(role.name))

	@add.command(pass_context=True, aliases=["nsfwchannel"])
	async def addnsfwchannel(self, ctx, *, channel: discord.Channel = None):
		self.servers = self.con.load_config()
		if channel.id not in self.servers[ctx.message.server.id]["nsfw"]["channels"]:
			self.servers[ctx.message.server.id]["nsfw"]["channels"].append(channel.id)
			self.con.update_config(self.servers)
			return await self.bot.say("'{}' has been added to the nsfw channel list.".format(channel.name))
		else:
			return await self.bot.say("'{}' is already in the list.".format(channel.name))

	@group(pass_context=True)
	@checks.is_owner_or_admin()
	async def remove(self, ctx):
		"OWNER OR ADMIN ONLY: Removes things like admin roles."
		if ctx.invoked_subcommand is None:
			return await self.bot.say('Missing Argument')

	@remove.command(pass_context=True, aliases=["adminrole"])
	async def readminrole(self, ctx, *, role: discord.Role = None):
		self.servers = self.con.load_config()
		try:
			self.servers[ctx.message.server.id]["perm_roles"]["admin"].remove(role.id)
		except ValueError:
			return await self.bot.say("That role was not in the list.")
		self.con.update_config(self.servers)
		return await self.bot.say("'{}' has been removed from the Admin role list.".format(role.name))

	@remove.command(pass_context=True, aliases=["modrole"])
	async def remodrole(self, ctx, *, role: discord.Role = None):
		self.servers = self.con.load_config()
		try:
			self.servers[ctx.message.server.id]["perm_roles"]["mod"].remove(role.id)
		except ValueError:
			return await self.bot.say("That role was not in the list.")
		self.con.update_config(self.servers)
		return await self.bot.say("'{}' has been removed from the Mod role list.".format(role.name))

	@remove.command(pass_context=True, aliases=["nsfwchannel"])
	async def rensfwchannel(self, ctx, *, channel: discord.Channel = None):
		self.servers = self.con.load_config()
		try:
			self.servers[ctx.message.server.id]["nsfw"]["channels"].remove(channel.id)
		except ValueError:
			return await self.bot.say("That role was not in the list.")
		self.con.update_config(self.servers)
		return await self.bot.say("'{}' has been removed from the nsfw channel list.".format(channel.name))

	@checks.is_admin_or_mod()
	@bot.command(pass_context=True)
	async def serverisanal(self, ctx):
		self.servers = self.con.load_config()
		is_anal = self.servers[ctx.message.server.id]["is_anal"]
		if is_anal:
			self.servers[ctx.message.server.id]["is_anal"]["y/n"] = 0
			self.con.update_config(self.servers)
			return await self.bot.say("I now know this server is anal")
		else:
			self.servers[ctx.message.server.id]["is_anal"]["y/n"] = 1
			self.con.update_config(self.servers)
			return await self.bot.say("I now know this server is NOT anal")


def setup(Bot):
	Bot.add_cog(Settings(Bot))