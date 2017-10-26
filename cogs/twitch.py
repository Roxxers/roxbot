import discord
from discord.ext.commands import group

import checks
from config.server_config import ServerConfig

def blacklisted(user):
	with open("config/blacklist.txt", "r") as fp:
		for line in fp.readlines():
			if user.id+"\n" == line:
				return True
	return False

class Twitch():
	"""
	A cog that handles posting when users go live on Twitch
	"""
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	async def on_member_update(self, member_b, member_a):
		# Twitch Shilling Part
		if blacklisted(member_b):
			return
		# Check to see if member_before game exists. Avoids crashes at line 24
		if member_b.game:
			typeb = member_b.game.type
		else:
			typeb = False
		if member_a.game:
			if member_a.game.type and not typeb: # Hopefully this fucking fixes it
				ts_enabled = self.servers[member_a.server.id]["twitch"]["enabled"]
				ts_whitelist = self.servers[member_a.server.id]["twitch"]["whitelist"]["enabled"]
				if ts_enabled:
					if not ts_whitelist or member_a.id in \
							self.servers[member_a.server.id]["twitch"]["whitelist"]["list"]:
						channel = discord.Object(self.servers[member_a.server.id]["twitch"]["twitch-channel"])
						return await self.bot.send_message(channel,
														   content=":video_game:** {} is live!** :video_game:\n{}\n{}".format(
															   member_a.name, member_a.game.name, member_a.game.url))
	@group(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def twitch(self, ctx):
		if ctx.invoked_subcommand is None:
			return await self.bot.say('Missing Argument')

	@twitch.command(pass_context=True, hidden=True)
	async def enablewhitelist(self, ctx):
		self.servers = self.con.load_config()
		if not self.servers[ctx.server.id]["twitch"]["whitelist"]["enabled"]:
			self.servers[ctx.server.id]["twitch"]["whitelist"]["enabled"] = 1
			self.con.update_config(self.servers)
			return await self.bot.reply("Whitelist for Twitch shilling has been enabled.")
		else:
			self.servers[ctx.server.id]["twitch"]["whitelist"]["enabled"] = 0
			self.con.update_config(self.servers)
			return await self.bot.reply("Whitelist for Twitch shilling has been disabled.")

	@twitch.command(pass_context=True, hidden=True)
	async def whitelistadd(self, ctx, option, *mentions):
		whitelist_count = 0

		if not ctx.message.mentions and option != 'list':
			return await self.bot.reply("You haven't mentioned anyone to whitelist.")

		if option not in ['+', '-', 'add', 'remove', 'list']:
			return await self.bot.say('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

		if option in ['+', 'add']:
			self.servers = self.con.load_config()
			for user in ctx.message.mentions:
				self.servers[ctx.message.server.id]["twitch"]["whitelist"]["list"].append(user.id)
				self.con.update_config(self.servers)
				whitelist_count += 1
			return await self.bot.say('{} user(s) have been added to the whitelist'.format(whitelist_count))

		elif option in ['-', 'remove']:
			self.servers = self.con.load_config()
			for user in ctx.message.mentions:
				if user.id in self.servers[ctx.message.server.id]["twitch"]["whitelist"]["list"]:
					self.servers[ctx.message.server.id]["twitch"]["whitelist"]["list"].remove(user.id)
					self.con.update_config(self.servers)
					whitelist_count += 1
			return await self.bot.say('{} user(s) have been removed to the whitelist'.format(whitelist_count))

		elif option == 'list':
			return await self.bot.say(
				self.servers[ctx.message.server.id]["twitch"]["whitelist"]["list"])


def setup(Bot):
	Bot.add_cog(Twitch(Bot))