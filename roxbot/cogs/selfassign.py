import discord
from discord.ext import commands

import roxbot
from roxbot import guild_settings as gs


class SelfAssign():
	def __init__(self, Bot):
		self.bot = Bot

	@commands.command(pass_context=True)
	async def listroles(self, ctx):
		"""
		List's all roles that can be self-assigned on this server.
		Usage:
			{command_prefix}listroles
		"""
		settings = gs.get(ctx.guild)
		if not settings.self_assign["enabled"]:
			embed = discord.Embed(colour=roxbot.EmbedColours.pink, description="SelfAssignable roles are not enabled on this server")
			return await ctx.send(embed=embed)
		roles = []
		for role in settings.self_assign["roles"]:
			for serverrole in ctx.guild.roles:
				if role == serverrole.id:
					roles.append("**"+serverrole.name+"**")
		roles = '\n'.join(roles)
		embed = discord.Embed(colour=roxbot.EmbedColours.pink, description="The self-assignable roles for this server are: \n"+roles)
		return await ctx.send(embed=embed)

	@commands.command(pass_context=True)
	async def iam(self, ctx, *, role: discord.Role = None):
		"""
		Self-assign yourself a role. Only one role at a time.
		Usage:
			{command_prefix}iam [role]
		Example:
			.iam OverwatchPing
		"""
		settings = gs.get(ctx.guild)

		if role is None:
			# Hacky way to get the error I want
			from inspect import Parameter
			raise commands.MissingRequiredArgument(Parameter("Role", False))

		if not settings.self_assign["enabled"]:
			embed = discord.Embed(colour=roxbot.EmbedColours.pink, description="SelfAssignable roles are not enabled on this server")
			return await ctx.send(embed=embed)

		member = ctx.author

		if role in member.roles:
			return await ctx.send("You already have that role.")

		if role.id in settings.self_assign["roles"]:
			await member.add_roles(role, reason="'iam' command triggered.")
			return await ctx.send("Yay {}! You now have the {} role!".format(member.mention, role.name))
		else:
			return await ctx.send("That role is not self-assignable.")

	@commands.command(pass_context=True)
	async def iamn(self, ctx, *, role: discord.Role = None):
		"""
		Remove a self-assigned role
		Usage:
			{command_prefix}iamn [role]
		Example:
			.iamn OverwatchPing
		"""
		settings = gs.get(ctx.guild)

		if role is None:
			from inspect import Parameter
			raise commands.MissingRequiredArgument(Parameter("role", False))

		if not settings.self_assign["enabled"]:
			embed = discord.Embed(colour=roxbot.EmbedColours.pink, description="SelfAssignable roles are not enabled on this server")
			return await ctx.send(embed=embed)

		member = ctx.author

		if role in member.roles and role.id in settings.self_assign["roles"]:
			await member.remove_roles(role, reason="'iamn' command triggered.")
			return await ctx.send("{} has been successfully removed.".format(role.name))
		elif role not in member.roles and role.id in settings.self_assign["roles"]:
			return await ctx.send("You do not have {}.".format(role.name))
		else:
			return await ctx.send("That role is not self-assignable.")


def setup(Bot):
	Bot.add_cog(SelfAssign(Bot))