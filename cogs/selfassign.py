import discord
from discord.ext import commands

import checks
from config.server_config import ServerConfig


class SelfAssign():
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
		if not self.servers[ctx.message.server.id]["self_assign"]["enabled"]:
			embed = discord.Embed(colour=discord.Colour(0xDEADBF),  # Make Embed colour a constant
								  description="SelfAssignable roles are not enabled on this server")
			return await self.bot.say(embed=embed)
		roles = []
		for role in self.servers[ctx.message.server.id]["self_assign"]["roles"]:
			for serverrole in ctx.message.server.roles:
				if role == serverrole.id:
					roles.append("**"+serverrole.name+"**")
		roles = '\n'.join(roles)
		embed = discord.Embed(colour=discord.Colour(0xDEADBF), # Make Embed colour a constant
							  description="The self-assignable roles for this server are: \n"+roles)
		return await self.bot.say(embed=embed)

	@commands.command(pass_context=True)
	async def iam(self, ctx, *, role: discord.Role = None):
		"""
		Self-assign yourself a role. Only one role at a time.
		Usage:
			{command_prefix}iam [role]
		Example:
			.iam OverwatchPing
		"""
		self.servers = self.con.load_config()
		if not self.servers[ctx.message.server.id]["self_assign"]["enabled"]:
			return

		user = ctx.message.author
		server = ctx.message.server

		if role not in server.roles:
			return await self.bot.say("That role doesn't exist. Roles are case sensitive. ")

		if role in user.roles:
			return await self.bot.say("You already have that role.")

		if role.id in self.servers[ctx.message.server.id]["self_assign"]["roles"]:
			await self.bot.add_roles(user, role)
			print("{} added {} to themselves in {} on {}".format(user.display_name, role.name, ctx.message.channel,
																 ctx.message.server))
			return await self.bot.say("Yay {}! You now have the {} role!".format(user.mention, role.name))
		else:
			return await self.bot.say("That role is not self-assignable.")

	@commands.command(pass_context=True)
	async def iamn(self, ctx, *, role: discord.Role = None):
		"""
		Remove a self-assigned role
		Usage:
			{command_prefix}iamn [role]
		Example:
			.iamn OverwatchPing
		"""
		self.servers = self.con.load_config()
		if not self.servers[ctx.message.server.id]["self_assign"]["enabled"]:
			print("Self Assign is Disabled")
			return

		user = ctx.message.author
		server = ctx.message.server

		if role not in server.roles:
			return await self.bot.say("That role doesn't exist. Roles are case sensitive. ")

		elif role in user.roles and role.id in self.servers[ctx.message.server.id]["self_assign"]["roles"]:
			print("passed in server check")
			await self.bot.remove_roles(user, role)
			return await self.bot.reply("{} has been successfully removed.".format(role.name))

		elif role not in user.roles and role.id in self.servers[ctx.message.server.id]["self_assign"]["roles"]:
			return await self.bot.reply("You do not have {}.".format(role.name))
		else:
			return await self.bot.say("That role is not self-assignable.")



def setup(Bot):
	Bot.add_cog(SelfAssign(Bot))