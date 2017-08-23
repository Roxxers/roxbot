import discord
from discord.ext import commands

from server_config import ServerConfig
import checks

class selfAssign():
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	@commands.command(pass_context=True)
	async def listroles(self, ctx):
		"""
		List's all roles that can be self-assigned on this server.
		Usage:
			{command_prefix}listroles
		"""
		roles = []
		for role in self.servers[ctx.message.server.id]["selfAssign"]["roles"]:
			for serverrole in ctx.message.server.roles:
				if role == serverrole.id:
					roles.append(serverrole.name)
		return await self.bot.say(str(roles).strip("[]"))

	@commands.command(pass_context=True)
	async def iam(self, ctx, role: discord.Role = None):
		"""
		Self-assign yourself a role. Only one role at a time. Doesn't work for roles with spaces.
		Usage:
			{command_prefix}iam [role]
		Example:
			.iam OverwatchPing
		"""
		self.servers = self.con.load_config()
		if not self.servers[ctx.message.server.id]["selfAssign"]["enabled"]:
			return

		user = ctx.message.author
		server = ctx.message.server

		if role not in server.roles:
			return await self.bot.say("That role doesn't exist. Roles are case sensitive. ")

		if role in user.roles:
			return await self.bot.say("You already have that role.")

		if role.id in self.servers[ctx.message.server.id]["selfAssign"]["roles"]:
			await self.bot.add_roles(user, role)
			print("{} added {} to themselves in {} on {}".format(user.display_name, role.name, ctx.message.channel,
																 ctx.message.server))
			return await self.bot.say("Yay {}! You now have the {} role!".format(user.mention, role.name))
		else:
			return await self.bot.say("That role is not self-assignable.")

	@commands.command(pass_context=True)
	async def iamn(self, ctx, role: discord.Role = None):
		"""
		Remove a self-assigned role
		Usage:
			{command_prefix}iamn [role]
		Example:
			.iamn OverwatchPing
		"""
		self.servers = self.con.load_config()
		if not self.servers[ctx.message.server.id]["selfAssign"]["enabled"]:
			return

		user = ctx.message.author
		server = ctx.message.server

		if role not in server.roles:
			return await self.bot.say("That role doesn't exist. Roles are case sensitive. ")

		elif role in user.roles and role.id in self.servers[ctx.message.server.id]["selfAssign"]["roles"]:
			await self.bot.remove_roles(user, role)
			return await self.bot.reply("{} has been successfully removed.".format(role.name))

		elif role not in user.roles and role.id in self.servers[ctx.message.server.id]["selfAssign"]["roles"]:
			return await self.bot.reply("You do not have {}.".format(role.name))
		else:
			return await self.bot.say("That role is not self-assignable.")

	@commands.command(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def addrole(self, ctx, role: discord.Role = None):
		self.servers = self.con.load_config()
		if role.id in self.servers[ctx.message.server.id]["selfAssign"]["roles"]:
			return await self.bot.say("{} is already a self-assignable role.".format(role.name), delete_after=self.con.delete_after)

		self.servers[ctx.message.server.id]["selfAssign"]["roles"].append(role.id)
		self.con.update_config(self.servers)
		return await self.bot.say('Role "{}" added'.format(str(role)))

	@commands.command(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def removerole(self, ctx, role: discord.Role = None):
		self.servers = self.con.load_config()
		if role.id in self.servers[ctx.message.server.id]["selfAssign"]["roles"]:
			self.servers[ctx.message.server.id]["selfAssign"]["roles"].remove(role.id)
			self.con.update_config(self.servers)
			return await self.bot.say('"{}" has been removed from the self-assignable roles.'.format(str(role)))
		else:
			return await self.bot.say("That role was not in the list.")

def setup(Bot):
	Bot.add_cog(selfAssign(Bot))