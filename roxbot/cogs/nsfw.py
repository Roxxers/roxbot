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


import discord
from discord.ext import commands

import roxbot
from roxbot import guild_settings as gs


def tag_blacklist(guild):
	blacklist = ""
	for tag in gs.get(guild)["nsfw"]["blacklist"]:
		blacklist += " -{}".format(tag)
	return blacklist


class NFSW(commands.Cog):
	"""The NSFW cog is a collection of commands that post images from popular NSFW sites. """
	def __init__(self, bot_client):
		self.bot = bot_client
		self.cache = {}
		self.settings = {
			"nsfw": {
				"enabled": 0,
				"convert": {"enabled": "bool"},
				"blacklist": []
			}
		}

	async def gelbooru_clone(self, ctx, base_url, endpoint_url, tags):
		if isinstance(ctx.channel, discord.TextChannel):
			banned_tags = tag_blacklist(ctx.guild)
		else:
			banned_tags = ""

		post = await roxbot.utils.danbooru_clone_api_req(
			ctx.channel,
			base_url,
			endpoint_url,
			tags=tags,
			banned_tags=banned_tags,
			cache=self.cache
		)

		if not post:
			return await ctx.send("Nothing was found. *psst, check the tags you gave me.*")
		else:
			output = await ctx.send(post)
			await self.bot.delete_option(output, self.bot.get_emoji(444410658101002261))

	@roxbot.checks.is_nsfw()
	@commands.command()
	async def e621(self, ctx, *, tags=""):
		"""Posts a random image from https://e621.net using the tags you provide. Tags can be anything you would use to search the site normally like author and ratings.
		https://e621.net limits searches to 6 tags via the API. Blacklisting a lot of tags may break this command.
		Examples:
			# Post a random image
			;e621
			# Post a random image with the tag "test"
			;e621 test
		"""
		base_url = "https://e621.net/post/index.json?tags="
		return await self.gelbooru_clone(ctx, base_url, "", tags)

	@roxbot.checks.is_nsfw()
	@commands.command()
	async def rule34(self, ctx, *, tags=""):
		"""Posts a random image from https://rule34.xxx/ using the tags you provide. Tags can be anything you would use to search the site normally like author and ratings.
		Examples:
			# Post a random image
			;rule34
			# Post a random image with the tag "test"
			;rule34 test
		"""
		base_url = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags="
		endpoint_url = "https://img.rule34.xxx/images/"
		return await self.gelbooru_clone(ctx, base_url, endpoint_url, tags)

	@roxbot.checks.is_nsfw()
	@commands.command()
	async def gelbooru(self, ctx, *, tags=""):
		"""Posts a random image from https://gelbooru.com using the tags you provide. Tags can be anything you would use to search the site normally like author and ratings.
		Examples:
			# Post a random image
			;gelbooru
			# Post a random image with the tag "test"
			;gelbooru test
		"""
		base_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="
		endpoint_url = "https://simg3.gelbooru.com/images/"
		return await self.gelbooru_clone(ctx, base_url, endpoint_url, tags)

	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.command()
	async def nsfw(self, ctx, setting, *, changes=None):
		"""Edits settings for the nsfw cog and other nsfw commands.

		Options:
			enable/disable: Enable/disables nsfw commands.
			addbadtag/removebadtag: Add/Removes blacklisted tags so that you can avoid em with the commands.
		
		Examples:
			# Enabled NSFW commands
			;nsfw enable
			# Add "test" as a blacklisted tag
			;nsfw addbadtag test
			# Remove "Roxbot" as a blacklisted tag
			;nsfw removebadtag Roxbot
		"""
		setting = setting.lower()
		settings = roxbot.guild_settings.get(ctx.guild)
		nsfw = settings["nsfw"]

		if setting == "enable":
			nsfw["enabled"] = 1
			await ctx.send("'nsfw' was enabled!")
		elif setting == "disable":
			nsfw["enabled"] = 0
			await ctx.send("'nsfw' was disabled :cry:")
		elif setting == "addbadtag":
			if changes not in nsfw["blacklist"]:
				nsfw["blacklist"].append(changes)
				await ctx.send("'{}' has been added to the blacklisted tag list.".format(changes))
			else:
				return await ctx.send("'{}' is already in the list.".format(changes))
		elif setting == "removebadtag":
			try:
				nsfw["blacklist"].remove(changes)
				await ctx.send("'{}' has been removed from the blacklisted tag list.".format(changes))
			except ValueError:
				return await ctx.send("That tag was not in the blacklisted tag list.")
		else:
			return await ctx.send("No valid option given.")
		return settings.update(nsfw, "nsfw")


def setup(bot_client):
	bot_client.add_cog(NFSW(bot_client))
