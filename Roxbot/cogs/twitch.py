import discord
from discord.ext import commands

from Roxbot import checks
from Roxbot.settings.guild_settings import ServerConfig

def blacklisted(user):
	with open("settings/blacklist.txt", "r") as fp:
		for line in fp.readlines():
			if user.id+"\n" == line:
				return True
	return False

class Twitch():
	"""
	A cog that handles posting when users go live on Twitch
	"""
	def __init__(self, bot_client):
		self.bot = bot_client
		self.con = ServerConfig()
		self.servers = self.con.servers

	async def on_member_update(self, member_b, member_a):
		# Twitch Shilling Part
		if blacklisted(member_b) or not self.servers[str(member_a.guild.id)]["twitch"]["enabled"]:
			return

		if member_a.activitiy:
			if member_a.activity.type == discord.ActivityType.streaming and member_b.activity.type != discord.ActivityType.streaming:
				ts_whitelist = self.servers[str(member_a.guild.id)]["twitch"]["whitelist"]["enabled"]
				if not ts_whitelist or member_a.id in self.servers[str(member_a.guild.id)]["twitch"]["whitelist"]["list"]:
					channel = self.bot.get_channel(self.servers[str(member_a.guild.id)]["twitch"]["twitch-channel"])
					return await channel.send(":video_game:** {} is live!** :video_game:\n{}\n{}".format(
														   member_a.name, member_a.game.name, member_a.game.url))

	@commands.group()
	@checks.is_admin_or_mod()
	async def whitelist(self, ctx):
		"""Command group that handles the twitch cog's whitelist."""
		if ctx.invoked_subcommand is None:
			return await ctx.send('Missing Argument')

	@whitelist.command()
	async def enable(self, ctx):
		"""Enables the twitch shilling whitelist. Repeat the command to disable.
		Usage:
			;whitelist enable"""
		self.servers = self.con.load_config()
		if not self.servers[str(ctx.guild.id)]["twitch"]["whitelist"]["enabled"]:
			self.servers[str(ctx.guild.id)]["twitch"]["whitelist"]["enabled"] = 1
			self.con.update_config(self.servers)
			return await ctx.send("Whitelist for Twitch shilling has been enabled.")
		else:
			self.servers[str(ctx.guild.id)]["twitch"]["whitelist"]["enabled"] = 0
			self.con.update_config(self.servers)
			return await ctx.send("Whitelist for Twitch shilling has been disabled.")

	@whitelist.command()
	async def edit(self, ctx, option, mentions = None):
		"""Adds or removes users to the whitelist. Exactly the same as the blacklist command in usage."""
		whitelist_count = 0

		if not ctx.message.mentions and option != 'list':
			return await ctx.send("You haven't mentioned anyone to whitelist.")

		if option not in ['+', '-', 'add', 'remove', 'list']:
			return await ctx.send('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

		if option in ['+', 'add']:
			self.servers = self.con.load_config()
			for user in ctx.message.mentions:
				self.servers[str(ctx.guild.id)]["twitch"]["whitelist"]["list"].append(user.id)
				whitelist_count += 1
			self.con.update_config(self.servers)
			return await ctx.send('{} user(s) have been added to the whitelist'.format(whitelist_count))

		elif option in ['-', 'remove']:
			self.servers = self.con.load_config()
			for user in ctx.message.mentions:
				if user.id in self.servers[str(ctx.guild.id)]["twitch"]["whitelist"]["list"]:
					self.servers[str(ctx.guild.id)]["twitch"]["whitelist"]["list"].remove(user.id)
					whitelist_count += 1
			self.con.update_config(self.servers)
			return await ctx.send('{} user(s) have been removed to the whitelist'.format(whitelist_count))

		elif option == 'list':
			return await ctx.send(self.servers[str(ctx.guild.id)]["twitch"]["whitelist"]["list"])


def setup(bot_client):
	bot_client.add_cog(Twitch(bot_client))
