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
import discord
from discord.ext import commands

import roxbot
from roxbot import guild_settings


async def log(guild, channel, command_name, **kwargs):
	"""Logs activity internally for Roxbot. Will only do anything if the server enables internal logging.

	This is mostly used for logging when certain commands are used that can be an issue for admins. Esp when Roxbot outputs
	something that could break the rules, then deletes their message.

	Params
	=======
	guild: discord.Guild
		Used to check if the guild has logging enabled
	channel: discord.TextChannel
	command_name: str
	kwargs: dict
		All kwargs and two other params will be added to the logging embed as fields, allowing you to customise the output

	"""
	logging = guild_settings.get(guild)["logging"]
	if logging["enabled"]:
		embed = discord.Embed(title="{} command logging".format(command_name), colour=roxbot.EmbedColours.pink)
		for key, value in kwargs.items():
			embed.add_field(name=key, value=value)
		return await channel.send(embed=embed)


class Logging:
	def __init__(self, bot_client):
		self.bot = bot_client
		self.settings = {
			"logging": {
				"enabled": 0,
				"convert": {"enabled": "bool", "channel": "channel"},
				"channel": 0
			}
		}

	async def on_member_join(self, member):
		logging = guild_settings.get(member.guild)["logging"]
		if logging["enabled"]:
			channel = self.bot.get_channel(logging["channel"])
			embed = discord.Embed(title="{} joined the server".format(member), colour=roxbot.EmbedColours.pink)
			embed.add_field(name="ID", value=member.id)
			embed.add_field(name="Mention", value=member.mention)
			embed.add_field(name="Date Account Created", value=roxbot.datetime_formatting.format(member.created_at))
			embed.add_field(name="Date Joined", value=roxbot.datetime_formatting.format(member.joined_at))
			embed.set_thumbnail(url=member.avatar_url)
			return await channel.send(embed=embed)

	async def on_member_remove(self, member):
		# TODO: Add some way of detecting whether a user left/was kicked or was banned.
		logging = guild_settings.get(member.guild)["logging"]
		if logging["enabled"]:
			channel = self.bot.get_channel(logging["channel"])
			embed = discord.Embed(description="{} left the server".format(member), colour=roxbot.EmbedColours.pink)
			return await channel.send(embed=embed)

	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	@commands.command(aliases=["log"])
	async def logging(self, ctx, setting, *, channel: typing.Optional[discord.TextChannel] = None):
		"""Edits the logging settings.

		Options:
			enable/disable: Enable/disables logging.
			channel: sets the channel.
		"""

		setting = setting.lower()
		settings = guild_settings.get(ctx.guild)

		if setting == "enable":
			settings["logging"]["enabled"] = 1
			await ctx.send("'logging' was enabled!")
		elif setting == "disable":
			settings["logging"]["enabled"] = 0
			await ctx.send("'logging' was disabled :cry:")
		elif setting == "channel":
			if not channel:
				channel = ctx.channel
			settings["logging"]["channel"] = channel.id
			await ctx.send("{} has been set as the logging channel!".format(channel.mention))
		else:
			return await ctx.send("No valid option given.")
		return settings.update(settings["logging"], "logging")


def setup(bot_client):
	bot_client.add_cog(Logging(bot_client))
