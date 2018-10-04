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


class Twitch():
	"""
	A cog that handles posting when users go live on Twitch
	"""
	def __init__(self, bot_client):
		self.bot = bot_client
		self.settings = {
			"twitch": {
				"enabled": 0,
				"convert": {"enabled": "bool", "channel": "channel", "whitelist_enabled": "bool", "whitelist": "user"},
				"channel": 0,
				"whitelist_enabled": 0,
				"whitelist": []
			}
		}

	async def on_member_update(self, member_b, member_a):
		"""Twitch Shilling Part"""
		twitch = roxbot.guild_settings.get(member_b.guild)["twitch"]
		if roxbot.blacklisted(member_b) or not twitch["enabled"]:
			return

		if member_a.activitiy:
			if member_a.activity.type == discord.ActivityType.streaming and member_b.activity.type != discord.ActivityType.streaming:
				if not twitch["whitelist"]["enabled"] or member_a.id in twitch["whitelist"]["list"]:
					channel = self.bot.get_channel(twitch["channel"])
					return await channel.send(":video_game:** {} is live!** :video_game:\n{}\n{}".format(
						member_a.name, member_a.game.name, member_a.game.url))

	@commands.guild_only()
	@commands.group(aliases=["wl"])
	@commands.has_permissions(manage_channels=True)
	async def whitelist(self, ctx):
		"""Command group that handles the twitch cog's whitelist."""
		if ctx.invoked_subcommand is None:
			return await ctx.send('Missing Argument')

	@whitelist.command()
	async def enable(self, ctx):
		"""Enables the twitch shilling whitelist. Repeat the command to disable.
		Usage:
			;whitelist enable"""
		settings = roxbot.guild_settings.get(ctx.guild)
		if not settings["twitch"]["whitelist"]["enabled"]:
			settings["twitch"]["whitelist"]["enabled"] = 1
			settings.update(settings["twitch"], "twitch")
			return await ctx.send("Whitelist for Twitch shilling has been enabled.")
		else:
			settings["twitch"]["whitelist"]["enabled"] = 0
			settings.update(settings["twitch"], "twitch")
			return await ctx.send("Whitelist for Twitch shilling has been disabled.")

	@whitelist.command()
	async def edit(self, ctx, option, mentions=None):
		"""Adds or removes users to the whitelist. Exactly the same as the blacklist command in usage."""

		# TODO: This is all horribly outdated useage and needs to be rewritten.

		whitelist_count = 0
		settings = roxbot.guild_settings.get(ctx.guild)

		if not ctx.message.mentions and option != 'list':
			return await ctx.send("You haven't mentioned anyone to whitelist.")

		if option not in ['+', '-', 'add', 'remove', 'list']:
			return await ctx.send('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

		if option in ['+', 'add']:
			for user in ctx.message.mentions:
				settings["twitch"]["whitelist"]["list"].append(user.id)
				whitelist_count += 1
			settings.update(settings["twitch"], "twitch")
			return await ctx.send('{} user(s) have been added to the whitelist'.format(whitelist_count))

		elif option in ['-', 'remove']:
			for user in ctx.message.mentions:
				if user.id in settings["twitch"]["whitelist"]["list"]:
					settings["twitch"]["whitelist"]["list"].remove(user.id)
					whitelist_count += 1
			settings.update(settings["twitch"], "twitch")
			return await ctx.send('{} user(s) have been removed to the whitelist'.format(whitelist_count))

		elif option == 'list':
			return await ctx.send(settings["twitch"]["whitelist"]["list"])

	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.command()
	async def twitch(self, ctx, setting, *, channel: discord.TextChannel = None):
		"""Edits settings for self assign cog.

		Options:
			enable/disable: Enable/disables the cog.
			channel: Sets the channel to shill in.
		"""

		setting = setting.lower()
		settings = roxbot.guild_settings.get(ctx.guild)
		twitch = settings["twitch"]

		if setting == "enable":
			twitch["enabled"] = 1
			await ctx.send("'twitch' was enabled!")
		elif setting == "disable":
			twitch["enabled"] = 0
			await ctx.send("'twitch' was disabled :cry:")
		elif setting == "channel":
			twitch["channel"] = channel.id
			await ctx.send("{} has been set as the twitch shilling channel!".format(channel.mention))
		else:
			return await ctx.send("No valid option given.")
		return settings.update(twitch, "twitch")


def setup(bot_client):
	bot_client.add_cog(Twitch(bot_client))
