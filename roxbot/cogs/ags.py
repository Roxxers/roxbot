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


import typing
import datetime

import discord
from discord.ext import commands

import roxbot


ags_id = 393764974444675073
selfieperms = 394939389823811584
nsfwimageperms = 394941004043649036
newbie = 450042170112475136


def is_ags():
	return commands.check(lambda ctx: ctx.guild.id == ags_id)


async def tatsumaki_api_call(member, guild):
	base = "https://api.tatsumaki.xyz/"
	url = base + "guilds/" + str(guild.id) + "/members/" + str(member.id) + "/stats"
	return await roxbot.http.api_request(url, headers={"Authorization": roxbot.tat_token})


class AsortedGenderSounds:
	def __init__(self, bot_client):
		self.bot = bot_client
		self.acceptable_roles = (nsfwimageperms, selfieperms)
		self.settings = {
			"limited_to_guild": str(ags_id),
			"ags": {
				"log_channel": "",
				"required_days": "",
				"required_score": "",
			}
		}

	async def on_member_join(self, member):
		if member.guild.id == ags_id:
			role = member.guild.get_role(newbie)
			await member.add_roles(role, reason="Auto-add role on join")
			await member.send("Please read our <#396697172139180033> and <#422514427263188993> channels. To gain access to the server, you must agree to the rules.")

	@commands.command()
	async def agree(self, ctx):
		role = ctx.guild.get_role(newbie)
		try:
			return await ctx.author.remove_roles(role, reason="User has agreed the rules and has been given access to the server.")
		except discord.HTTPException:
			pass

	@commands.command(hidden=True)
	async def perms(self, ctx, role):
		"""Shell command to do the perm assigning. Only should be invoked by another command."""
		# Just in case some cunt looks at the source code and thinks they can give themselves Admin.
		if role.id not in self.acceptable_roles:
			return False
		settings = roxbot.guild_settings.get(ctx.guild)
		member = ctx.author
		required_score = settings["ags"]["required_score"]
		days = int(settings["ags"]["required_days"])
		data = await tatsumaki_api_call(member, ctx.guild)
		if data is None:
			return await ctx.send("Tatsumaki API call returned nothing. Maybe the API is down?")

		if role in member.roles:
			await member.remove_roles(role, reason="Requested removal of {0.name}".format(role))
			return await ctx.send("You already had {0.name}. It has now been removed.".format(role))

		time = datetime.datetime.now() - ctx.author.joined_at

		if time > datetime.timedelta(days=days) and int(data["score"]) >= required_score:
			await member.add_roles(role, reason="Requested {0.name}".format(role))
			await ctx.send("You have now have the {0.name} role".format(role))
		else:
			return await ctx.send(
				"You do not meet the requirements for this role. You need at least {} score with <@!172002275412279296> and to have been in the server for {} days.".format(required_score, days)
			)

	@is_ags()
	@commands.command()
	async def selfieperms(self, ctx):
		"""Requests the selfie perm role."""
		arg = None
		for role in ctx.guild.roles:
			if role.id == selfieperms:
				arg = role
		if not arg:
			return ctx.send("Error, message roxie thanks.")
		return await ctx.invoke(self.perms, role=arg)

	#@is_not_nsfw_disabled()
	@is_ags()
	@commands.command(hidden=True, enabled=False)
	async def nsfwperms(self, ctx):
		"""Requests the NSFW Image Perm role."""
		arg = None
		for role in ctx.guild.roles:
			if role.id == nsfwimageperms:
				arg = role
		if not arg:
			return ctx.send("Error, message roxie thanks.")
		return await ctx.invoke(self.perms, role=arg)

	@commands.command()
	async def ags(self, ctx, selection, amount: typing.Optional[int], *, channel: typing.Optional[discord.TextChannel] = None):
		"""Custom Cog for the GaySoundsShitposts Discord Server."""
		selection = selection.lower()
		settings = roxbot.guild_settings.get(ctx.guild)
		ags = settings["ags"]

		if selection == "loggingchannel":
			if not channel:
				channel = ctx.channel
			elif ctx.message.channel_mentions:
				channel = ctx.channel_mentions[0]
			else:
				channel = ctx.guild.get_channel(channel)
			ags["log_channel"] = channel.id
			await ctx.send("Logging Channel set to '{}'".format(channel.name))
		elif selection == "requireddays":
			ags["required_days"] = amount
			await ctx.send("Required days set to '{}'".format(str(amount)))
		elif selection == "requiredscore":
			ags["required_score"] = amount
			await ctx.send("Required score set to '{}'".format(str(amount)))
		else:
			return await ctx.send("No valid option given.")
		return settings.update(ags, "ags")


def setup(bot_client):
	bot_client.add_cog(AsortedGenderSounds(bot_client))
