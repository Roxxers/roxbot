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


import discord
from discord.ext import commands

import roxbot
from roxbot import guild_settings as gs


class SelfAssign():
	def __init__(self, Bot):
		self.bot = Bot

	async def on_guild_role_delete(self, role):
		settings = gs.get(role.guild)
		sa = settings.self_assign
		for sa_role in sa["roles"]:
			if int(sa_role) == role.id:
				sa["roles"].remove(role.id)
				return settings.update(sa, "self_assign")

	@commands.guild_only()
	@commands.command(pass_context=True)
	async def listroles(self, ctx):
		"""
		List's all roles that can be self-assigned on this server.
		Usage:
			{command_prefix}listroles
		"""
		settings = gs.get(ctx.guild)
		paginator = commands.Paginator(prefix="`", suffix="`")

		if not settings.self_assign["enabled"]:
			embed = discord.Embed(colour=roxbot.EmbedColours.pink, description="SelfAssignable roles are not enabled on this server")
			return await ctx.send(embed=embed)

		paginator.add_line("The self-assignable roles for this server are: \n")
		for role in settings.self_assign["roles"]:
			for serverrole in ctx.guild.roles:
				if role == serverrole.id:
					paginator.add_line("- {}".format(serverrole.name))

		for page in paginator.pages:
			await ctx.send(page)

	@commands.guild_only()
	@commands.command(pass_context=True)
	async def iam(self, ctx, *, role: discord.Role):
		"""
		Self-assign yourself a role. Only one role at a time. # TODO: Experiment with special converters here.
		Usage:
			{command_prefix}iam [role]
		Example:
			.iam OverwatchPing
		"""
		settings = gs.get(ctx.guild)

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

	@commands.guild_only()
	@commands.command(pass_context=True)
	async def iamn(self, ctx, *, role: discord.Role):
		"""
		Remove a self-assigned role
		Usage:
			{command_prefix}iamn [role]
		Example:
			.iamn OverwatchPing
		"""
		settings = gs.get(ctx.guild)

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
