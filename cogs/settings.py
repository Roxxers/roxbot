import os
import sys
import json
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
	Settings is a mix of settings and admin stuff for the bot.
	"""
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	@bot.command(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def blacklist(self, ctx, option, *args):
		"""
		Usage:
			.blacklist [ + | - | add | remove ] @UserName [@UserName2 ...]
		Add or remove users to the blacklist.
		Blacklisted users are forbidden from using bot commands.
		Only the bot owner can use this command
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


	@bot.command(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def enablesetting(self, ctx, setting):
		server_id = ctx.message.server.id
		if setting in self.serverconfig[server_id]:
			self.serverconfig = self.con.load_config()
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

	@bot.command(pass_context=True)
	@checks.is_bot_owner()
	async def printsettings(self, ctx):
		self.serverconfig = self.con.load_config()
		config = self.serverconfig[ctx.message.server.id]
		em = discord.Embed(colour=0xDEADBF)
		em.set_author(name="RoxBot settings for {}.".format(ctx.message.server.name), icon_url=self.bot.user.avatar_url)

		for settings in config:
			settingcontent = ""
			for x in config[settings].items():
				settingcontent += str(x).strip("()") + "\n"
			em.add_field(name=settings, value=settingcontent)

		return await self.bot.say(embed=em)

	@group(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def set(self, ctx):
		if ctx.invoked_subcommand is None:
			return await self.bot.say('Missing Argument')

	@set.command(pass_context=True, hidden=True)
	async def welcomechannel(self, ctx, channel: discord.Channel = None):
		self.serverconfig = self.con.load_config()
		self.serverconfig[ctx.message.server.id]["greets"]["welcome-channel"] = channel.id
		self.con.update_config(self.serverconfig)
		return await self.bot.say("{} has been set as the welcome channel!".format(channel.mention))

	@set.command(pass_context=True, hidden=True)
	async def goodbyechannel(self, ctx, channel: discord.Channel = None):
		self.serverconfig = self.con.load_config()
		self.serverconfig[ctx.message.server.id]["goodbyes"]["goodbye-channel"] = channel.id
		self.con.update_config(self.serverconfig)
		return await self.bot.say("{} has been set as the goodbye channel!".format(channel.mention))

	@set.command(pass_context=True, hidden=True)
	async def twitchchannel(self, ctx, channel: discord.Channel = None):
		self.serverconfig = self.con.load_config()
		self.serverconfig[ctx.message.server.id]["twitch"]["twitch-channel"] = channel.id
		self.con.update_config(self.serverconfig)
		return await self.bot.say("{} has been set as the twitch shilling channel!".format(channel.mention))

	@set.command(pass_context=True, hidden=True)
	async def welcomemessage(self, ctx, *, message: str):
		self.serverconfig = self.con.load_config()
		self.serverconfig[ctx.message.server.id]["greets"]["custom-message"] = message
		self.con.update_config(self.serverconfig)
		return await self.bot.say("Custom message set to '{}'".format(message))

	@set.command(pass_context=True, hidden=True)
	async def muterole(self, ctx, role: discord.Role = None):
		self.serverconfig = self.con.load_config()
		self.serverconfig[ctx.message.server.id]["mute"]["role"] = role.id
		self.con.update_config(self.serverconfig)
		return await self.bot.say("Muted role set to '{}'".format(role.name))

	@set.command(pass_context=True, hidden=True)
	async def muteadmin(self, ctx, role: discord.Role = None):
		self.serverconfig = self.con.load_config()
		self.serverconfig[ctx.message.server.id]["mute"]["admin-role"].append(role.id)
		self.con.update_config(self.serverconfig)
		return await self.bot.say("Admin role appended to list: '{}'".format(role.name))

	@bot.command(pass_context=True, hidden=True, aliases=["setava"])
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

		avaimg = 'avaimg.png'
		async with aiohttp.ClientSession() as session:
			with session.get(thing) as img:
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
			game_name = discord.Game(name=game)
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

	@bot.command(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def echo(self, ctx, channel, *, message: str):
		if ctx.message.channel_mentions:
			for channel in ctx.message.channel_mentions:
				await self.bot.send_message(channel, content=message)
			return await self.bot.say(":point_left:")
		elif channel.isdigit():
			channel = ctx.message.server.get_channel(channel)
			await self.bot.send_message(channel, content=message)
			return await self.bot.say(":point_left:")
		else:
			return await self.bot.say("You did something wrong smh")

	@bot.command(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def restart(self, ctx):
		await self.bot.logout()
		return os.execl(sys.executable, sys.executable, *sys.argv)

	@bot.command(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def shutdown(self, ctx):
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


def setup(Bot):
	Bot.add_cog(Settings(Bot))