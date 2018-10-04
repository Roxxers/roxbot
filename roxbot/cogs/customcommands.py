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

import random
import discord
from discord.ext import commands

import roxbot


class CustomCommands:
	ERROR_AT_MENTION = "Custom Commands cannot mention people/roles/everyone."
	ERROR_COMMAND_NULL = "That Custom Command doesn't exist."
	ERROR_COMMAND_EXISTS = "Custom Command already exists."
	ERROR_COMMAND_EXISTS_INTERNAL = "This is already the name of a built in command."
	ERROR_EMBED_VALUE = "Not enough options given to generate embed."
	ERROR_INCORRECT_TYPE = "Incorrect type given."
	ERROR_OUTPUT_TOO_LONG = "Failed to set output. Given output was too long."
	ERROR_PREFIX_SPACE = "Custom commands with a prefix can only be one word with no spaces."

	OUTPUT_ADD = "{} has been added with the output: '{}'"
	OUTPUT_EDIT = "Edit made. {} now outputs {}"
	OUTPUT_REMOVE = "Removed {} custom command"

	def __init__(self, bot_client):
		self.bot = bot_client
		self.embed_fields = ("title", "description", "colour", "color", "footer", "image", "thumbnail", "url")
		self.settings = {
			"custom_commands": {
				"0": {},
				"1": {},
				"2": {},
				"convert": {"0": "hide", "1": "hide", "2": "hide"}
			}
		}

	@staticmethod
	def _get_output(command):
		# Check for a list as the output. If so, randomly select a item from the list.
		if isinstance(command, list):
			command = random.choice(command)
		return command

	@staticmethod
	def _embed_values(command_output):
		# discord.Embed.Empty is used by discord.py to denote when a field is empty. Hence why it is the fallback here
		title = command_output.get("title", discord.Embed.Empty)
		desc = command_output.get("description", discord.Embed.Empty)
		# Check for both possible colour fields. Then strip possible # and convert to hex for embed
		colour = command_output.get("colour", discord.Embed.Empty) or command_output.get("color", discord.Embed.Empty)
		if isinstance(colour, str):
			colour = discord.Colour(int(colour.strip("#"), 16))
		url = command_output.get("url", discord.Embed.Empty)
		footer = command_output.get("footer", discord.Embed.Empty)
		image = command_output.get("image", discord.Embed.Empty)
		thumbnail = command_output.get("thumbnail", discord.Embed.Empty)
		embed = discord.Embed(title=title, description=desc, colour=colour, url=url)
		if footer:
			embed.set_footer(text=footer)
		if image:
			embed.set_image(url=image)
		if thumbnail:
			embed.set_thumbnail(url=thumbnail)
		return embed

	def _embed_parse_options(self, options):
		# Create an dict from a list, taking each two items as a key value pair
		output = {item: options[index + 1] for index, item in enumerate(options) if index % 2 == 0}
		for key in output.copy().keys():
			if key not in self.embed_fields:
				output.pop(key)
		# Check for errors in inputs that would stop embed from being posted.
		title = output.get("title", "")
		desc = output.get("description", "")
		if len(title) > 256 or len(desc) > 256:
			raise ValueError

		# We only need one so purge the inferior spelling
		if "colour" in output and "color" in output:
			output.pop("color")
		return output

	async def on_message(self, message):
		# Limits customcommands to pm's as customcommands are handled at a guild level.
		if roxbot.blacklisted(message.author) or not isinstance(message.channel, discord.TextChannel):
			return
		if message.author == self.bot.user:
			return

		settings = roxbot.guild_settings.get(message.guild)
		msg = message.content.lower()
		channel = message.channel

		if msg.startswith(self.bot.command_prefix):
			command = msg.split(self.bot.command_prefix)[1]
			if command in settings["custom_commands"]["1"]:
				command_output = self._get_output(settings["custom_commands"]["1"][command])
				return await channel.send(command_output)

			elif command in settings["custom_commands"]["2"]:
				command_output = self._get_output(settings["custom_commands"]["2"][command])
				embed = self._embed_values(command_output)
				return await channel.send(embed=embed)
		else:
			for command in settings["custom_commands"]["0"]:
				if msg == command:
					command_output = self._get_output(settings["custom_commands"]["0"][command])
					return await channel.send(command_output)

	@commands.guild_only()
	@commands.group(aliases=["cc"])
	async def custom(self, ctx):
		""""
		A group of commands to manage custom commands for your server.
		Requires the Manage Messages permission.
		"""
		if ctx.invoked_subcommand is None:
			return await ctx.send('Missing Argument')

	@commands.has_permissions(manage_messages=True)
	@custom.command()
	async def add(self, ctx, command_type, command, *output):
		"""Adds a custom command to the list of custom commands."""
		# TODO: Better command docstring for better help with embeds
		if command_type in ("0", "no_prefix", "no prefix"):
			command_type = "0"
			if len(output) == 1:
				output = output[0]
		elif command_type in ("1", "prefix"):
			command_type = "1"
			if len(output) == 1:
				output = output[0]
		elif command_type in ("2", "embed"):
			command_type = "2"
			if len(output) < 2:
				raise roxbot.UserError(self.ERROR_EMBED_VALUE)
			try:
				output = self._embed_parse_options(output)
			except ValueError:
				raise roxbot.UserError(self.ERROR_OUTPUT_TOO_LONG)
		else:
			raise roxbot.UserError(self.ERROR_INCORRECT_TYPE)

		settings = roxbot.guild_settings.get(ctx.guild)
		no_prefix_commands = settings["custom_commands"]["0"]
		prefix_commands = settings["custom_commands"]["1"]
		embed_commands = settings["custom_commands"]["2"]
		command = command.lower()

		if ctx.message.mentions or ctx.message.mention_everyone or ctx.message.role_mentions:
			raise roxbot.UserError(self.ERROR_AT_MENTION)
		elif len(output) > 1800:
			raise roxbot.UserError(self.ERROR_OUTPUT_TOO_LONG)
		elif command in self.bot.all_commands.keys() and command_type == "1":
			raise roxbot.UserError(self.ERROR_COMMAND_EXISTS_INTERNAL)
		elif command in no_prefix_commands or command in prefix_commands or command in embed_commands:
			raise roxbot.UserError(self.ERROR_COMMAND_EXISTS)
		elif len(command.split(" ")) > 1 and command_type == "1":
			raise roxbot.UserError(self.ERROR_PREFIX_SPACE)

		settings["custom_commands"][command_type][command] = output
		settings.update(settings["custom_commands"], "custom_commands")
		return await ctx.send(self.OUTPUT_ADD.format(command, output))

	@commands.has_permissions(manage_messages=True)
	@custom.command()
	async def edit(self, ctx, command, *edit):
		""""Edits an existing custom command."""
		settings = roxbot.guild_settings.get(ctx.guild)
		no_prefix_commands = settings["custom_commands"]["0"]
		prefix_commands = settings["custom_commands"]["1"]
		embed_commands = settings["custom_commands"]["2"]

		if ctx.message.mentions or ctx.message.mention_everyone or ctx.message.role_mentions:
			raise roxbot.UserError(self.ERROR_AT_MENTION)

		if command in no_prefix_commands:
			if len(edit) == 1:
				edit = edit[0]
			settings["custom_commands"]["0"][command] = edit
			settings.update(settings["custom_commands"], "custom_commands")
			return await ctx.send(self.OUTPUT_EDIT.format(command, edit))

		elif command in prefix_commands:
			if len(edit) == 1:
				edit = edit[0]
			settings["custom_commands"]["1"][command] = edit
			settings.update(settings["custom_commands"], "custom_commands")
			return await ctx.send(self.OUTPUT_EDIT.format(command, edit))

		elif command in embed_commands:
			if len(edit) < 2:
				raise roxbot.UserError(self.ERROR_EMBED_VALUE)
			try:
				edit = self._embed_parse_options(edit)
			except ValueError:
				raise roxbot.UserError(self.ERROR_OUTPUT_TOO_LONG)
			settings["custom_commands"]["2"][command] = edit
			settings.update(settings["custom_commands"], "custom_commands")
			return await ctx.send(self.OUTPUT_EDIT.format(command, edit))

		else:
			raise roxbot.UserError(self.ERROR_COMMAND_NULL)

	@commands.has_permissions(manage_messages=True)
	@custom.command()
	async def remove(self, ctx, command):
		""""Removes a custom command."""
		settings = roxbot.guild_settings.get(ctx.guild)

		command = command.lower()
		no_prefix_commands = settings["custom_commands"]["0"]
		prefix_commands = settings["custom_commands"]["1"]
		embed_commands = settings["custom_commands"]["2"]

		if command in no_prefix_commands:
			command_type = "0"
		elif command in prefix_commands:
			command_type = "1"
		elif command in embed_commands:
			command_type = "2"
		else:
			raise roxbot.UserError(self.ERROR_COMMAND_NULL)

		settings["custom_commands"][command_type].pop(command)
		settings.update(settings["custom_commands"], "custom_commands")
		return await ctx.send(self.OUTPUT_REMOVE.format(command))

	@custom.command()
	async def list(self, ctx, debug="0"):
		""""Lists all custom commands for this server."""
		if debug != "0" and debug != "1":
			debug = "0"
		settings = roxbot.guild_settings.get(ctx.guild)
		cc = settings["custom_commands"]
		no_prefix_commands = cc["0"]
		prefix_commands = {**cc["1"], **cc["2"]}

		paginator = commands.Paginator()
		paginator.add_line("Here is the list of Custom Commands...")
		paginator.add_line()

		paginator.add_line("Commands that require Prefix:")
		if not prefix_commands:
			paginator.add_line("There are no commands setup.")
		else:
			for command in prefix_commands:
				if debug == "1":
					command += " = '{}'".format(prefix_commands[command])
				paginator.add_line("- " + command)

		paginator.add_line()
		paginator.add_line("Commands that don't require prefix:")
		if not no_prefix_commands:
			paginator.add_line("There are no commands setup.")
		else:
			for command in no_prefix_commands:
				if debug == "1":
					command += " = '{}'".format(no_prefix_commands[command])
				paginator.add_line("- " + command)

		output = paginator.pages
		for page in output:
			await ctx.send(page)


def setup(bot_client):
	bot_client.add_cog(CustomCommands(bot_client))
