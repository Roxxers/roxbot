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


import random
import asyncio
import discord
import argparse

from roxbot import http
from roxbot import guild_settings
from roxbot.enums import EmbedColours


class ArgParser(argparse.ArgumentParser):
	"""Create Roxbot's own version of ArgumentParser that doesn't exit the program on error."""
	def error(self, message):
		# By passing here, it will just continue in cases where a user inputs an arg that can't be parsed.
		pass


class Menu:

	__slots__ = ["name", "params", "formatted_params", "title", "content"]

	def __init__(self, name,  *params, settings=None):
		self.name = name
		self.params = list(params).append("Exit")
		if settings:
			self.formatted_params = self._parse_params(settings, self.name)
		else:
			self.formatted_params = self.params
		self.title = "'Roxbot Settings: {}'\n".format(self.name)
		self.content = self._format_content(self.title, self.formatted_params, "```python", "```")

	@staticmethod
	def _format_content(title, params, prefix="", suffix=""):
		separator = "—————————————————————————————"
		choices = "\n"
		for x, setting in enumerate(params):
			if setting == "Exit":
				choices += "[0] Exit\n"
			elif setting != "convert":
				if setting != [*params][x]:  # Just in case params is dict_keys, we make a new list.
					choices += "[{}] {}\n".format(x + 1, setting)
				else:
					choices += "[{}] Edit '{}'\n".format(x+1, setting)
		return prefix + title + separator + choices + suffix

	@staticmethod
	def _parse_params(settings, name):
		params = [*settings.keys()]
		params_copy = settings.copy().keys()
		for param in params_copy:
			if settings["convert"].get(param) == "bool":
				# Enable/Disable Parse
				if param == "enabled":
					options = ["Enable '{}'".format(name), "Disable '{}'".format(name)]
				else:
					options = ["Enable '{}'".format(param), "Disable '{}'".format(param)]
				params.remove(param)
				params = [*options, *params]
			elif isinstance(settings.get(param), list):
				# Add and Remove Parse
				options = ["Add {}".format(param), "Remove {}".format(param)]
				params.remove(param)
				params = [*params, *options]
			elif isinstance(settings.get(param), (int, str)):
				# Set parse
				options = "Set {}".format(param)
				params.remove(param)
				params = [*params, options]
		return params


async def delete_option(bot, ctx, message, delete_emoji, timeout=20):
	"""Utility function that allows for you to add a delete option to the end of a command.
	This makes it easier for users to control the output of commands, esp handy for random output ones.

	Params
	=======
	bot: discord.ext.commands.Bot
		The current bot client
	ctx: discord.ext.commands.Context
		The context of the command
	message: discord.Message
		Output message from Roxbot
	delete_emoji: discord.Emoji or str if unicode emoji
		Used as the reaction for the user to click on.
	timeout: int (Optional)
		Amount of time in seconds for the bot to wait for the reaction. Deletes itself after the timer runes out.
		Set to 20 by default
	"""
	await message.add_reaction(delete_emoji)

	def check(r, u):
		return str(r) == str(delete_emoji) and u == ctx.author and r.message.id == message.id

	try:
		await bot.wait_for("reaction_add", timeout=timeout, check=check)
		await message.remove_reaction(delete_emoji, bot.user)
		try:
			await message.remove_reaction(delete_emoji, ctx.author)
		except discord.Forbidden:
			pass
		await message.edit(content="{} requested output be deleted.".format(ctx.author), embed=None)
	except asyncio.TimeoutError:
		await message.remove_reaction(delete_emoji, bot.user)


def blacklisted(user):
	"""Checks if given user is blacklisted from the bot.
	Params
	=======
	user: discord.User

	Returns
	=======
	If the user is blacklisted: bool"""
	with open("roxbot/settings/blacklist.txt", "r") as fp:
		for line in fp.readlines():
			if str(user.id)+"\n" == line:
				return True
	return False


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
		embed = discord.Embed(title="{} command logging".format(command_name), colour=EmbedColours.pink)
		for key, value in kwargs.items():
			embed.add_field(name=key, value=value)
		return await channel.send(embed=embed)


async def danbooru_clone_api_req(channel, base_url, endpoint_url, cache=None, tags="", banned_tags=""):
	"""Utility function that deals with danbooru clone api interaction.
	It also deals with cache management for these interactions.

	Params
	=======
	channel: discord.Channel
		Channel command has been invoked in
	base_url: str
		Base url of the site
	endpoint_url: str
		Endpoint of images in the API. This is used if the API does not give this in its response.
	cache: dict (optional)
		Post cache. Were channel ID's are keys with values that are lists of identifiable info.
		Cache is handled in this function and will be updated so that other functions can access it.
	tags: str (optional)
		tags to use in the search. Separated by spaces.
	banned_tags: str (optional)
		banned tags to append to the search. Separated by spaces with a - in front to remove them from search results.
	"""
	limit = "150"
	tags = tags + banned_tags
	page_number = str(random.randrange(20))
	url = base_url + tags + '&limit=' + limit + '%pid=' + page_number

	if isinstance(channel, discord.DMChannel):
		cache_id = channel.id
	else:
		cache_id = channel.guild.id

	# IF ID is not in cache, create cache for ID
	if not cache.get(cache_id, False):
		cache[cache_id] = []

	posts = await http.api_request(url)

	if posts is None:
		return None

	post = None
	counter = 0
	while counter < 20:
		post = random.choice(posts)
		md5 = post.get("md5") or post.get("hash")
		if md5 not in cache[cache_id]:
			cache[cache_id].append(md5)
			if len(cache[cache_id]) > 10:
				cache[cache_id].pop(0)
			break
		counter += 1

	url = post.get("file_url")
	if not url:
		url = endpoint_url + "{0[directory]}/{0[image]}".format(post)
	return url
