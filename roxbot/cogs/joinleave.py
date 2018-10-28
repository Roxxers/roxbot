# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017-2018 Roxanne Gibson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import typing
import discord
from discord.ext import commands

import roxbot
from roxbot import guild_settings


class JoinLeave():
	def __init__(self, Bot):
		self.bot = Bot
		self.settings = {
			"greets": {
					"enabled": 0,
					"convert": {"enabled": "bool", "welcome-channel": "channel"},
					"welcome-channel": 0,
					"custom-message": "",
					"default-message": "Be sure to read the rules."
					},
				"goodbyes": {
					"enabled": 0,
					"convert": {"enabled": "bool", "goodbye-channel": "channel"},
					"goodbye-channel": 0,
					}
			}

	async def on_member_join(self, member):
		"""
		Greets users when they join a server.
		"""
		settings = guild_settings.get(member.guild)
		if not settings["greets"]["enabled"]:
			return

		if settings["greets"]["custom-message"]:
			message = settings["greets"]["custom-message"]
		else:
			message = settings["greets"]["default-message"]
		em = discord.Embed(
			title="Welcome to {}!".format(member.guild),
			description='Hey {}! Welcome to **{}**! {}'.format(member.mention, member.guild, message),
			colour=roxbot.EmbedColours.pink)
		em.set_thumbnail(url=member.avatar_url)

		channel = member.guild.get_channel(settings["greets"]["welcome-channel"])
		return await channel.send(embed=em)

	async def on_member_remove(self, member):
		"""
		The same but the opposite
		"""
		settings = guild_settings.get(member.guild)
		channel = settings["goodbyes"]["goodbye-channel"]
		if not settings["goodbyes"]["enabled"]:
			return
		else:
			channel = member.guild.get_channel(channel)
			return await channel.send(embed=discord.Embed(
				description="{}#{} has left or been beaned.".format(member.name, member.discriminator), colour=roxbot.EmbedColours.pink))

	async def on_guild_channel_delete(self, channel):
		"""Cleans up settings on removal of stored IDs."""
		settings = guild_settings.get(channel.guild)
		greets = settings["greets"]
		goodbyes = settings["goodbyes"]
		if channel.id == greets["welcome-channel"]:
			greets["welcome-channel"] = 0
			settings.update(greets, "greets")
		if channel.id == goodbyes["goodbye-channel"]:
			goodbyes["goodbye-channel"] = 0
			settings.update(goodbyes, "goodbyes")

	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def greets(self, ctx, setting, channel: typing.Optional[discord.TextChannel] = None, *, text: str):
		"""Edits settings for the Welcome Messages

		Options:
			enable/disable: Enable/disables parts of the cog. Needs to specify which part.
			channel: Sets the channels for either option. Must be a ID or mention.
			message: specifies a custom message for the greet messages.
		"""
		setting = setting.lower()
		settings = guild_settings.get(ctx.guild)
		greets = settings["greets"]
		if setting == "enable":
			greets["enabled"] = 1
			await ctx.send("'greets' was enabled!")
		elif setting == "disable":
			greets["enabled"] = 0
			await ctx.send("'greets' was disabled :cry:")
		elif setting == "channel":
			if channel is None:
				channel = ctx.channel
			greets["welcome-channel"] = channel.id
		elif setting == "custommessage":
			greets["custom-message"] = text
			await ctx.send("Custom message set to '{}'".format(text))
		else:
			return await ctx.send("No valid option given.")
		return settings.update(greets, "greets")

	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def goodbyes(self, ctx, setting, *, channel: typing.Optional[discord.TextChannel] = None):
		"""Edits settings for the Welcome Messages

		Options:
			enable/disable: Enable/disables parts of the cog. Needs to specify which part.
			channel: Sets the channels for either option. Must be a ID or mention.
			message: specifies a custom message for the greet messages.
		"""
		setting = setting.lower()
		settings = guild_settings.get(ctx.guild)
		goodbyes = settings["goodbyes"]
		if setting == "enable":
			goodbyes["enabled"] = 1
			await ctx.send("'goodbyes' was enabled!")
		elif setting == "disable":
			goodbyes["enabled"] = 0
			await ctx.send("'goodbyes' was disabled :cry:")
		elif setting == "channel":
			if channel is None:
				channel = ctx.channel
			goodbyes["goodbye-channel"] = channel.id
		else:
			return await ctx.send("No valid option given.")
		return settings.update(goodbyes, "goodbyes")

def setup(Bot):
	Bot.add_cog(JoinLeave(Bot))
