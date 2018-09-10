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


class CustomCommands:
	def __init__(self, bot_client):
		self.bot = bot_client

	async def on_message(self, message):
		if isinstance(message.channel, discord.DMChannel):
			return
		settings = roxbot.guild_settings.get(message.guild)
		msg = message.content.lower()
		channel = message.channel

		if roxbot.blacklisted(message.author) or type(message.channel) != discord.TextChannel:
			return
		if message.author == self.bot.user:
			return

		command = msg.split(self.bot.command_prefix)[1]
		if msg.startswith(self.bot.command_prefix):
			if command in settings.custom_commands["1"]:
				return await channel.send(settings.custom_commands["1"][command])
			elif command in settings.custom_commands["2"]:
				return await channel.send(settings.custom_commands["2"][command])
		else:
			for command in settings.custom_commands["0"]:
				if msg == command:
					return await channel.send(settings.custom_commands["0"][command])

	@commands.group(aliases=["cc"])
	@roxbot.checks.is_owner_or_admin()
	async def custom(self, ctx):
		""""A group of commands to manage custom commands for your server."""
		if ctx.invoked_subcommand is None:
			return await ctx.send('Missing Argument')

	@custom.command(pass_context=True)
	async def add(self, ctx, command_type, command, *output):
		"""Adds a custom command to the list of custom commands."""
		if command_type in ("0", "no_prefix", "no prefix"):
			command_type = "0"
		elif command_type in ("1", "prefix"):
			command_type = "1"
		elif command_type in ("2", "embed"):
			command_type = "2"
		else:
			return await ctx.send("Incorrect type given.")

		settings = roxbot.guild_settings.get(ctx.guild)
		no_prefix_commands = settings.custom_commands["0"]
		prefix_commands = settings.custom_commands["1"]
		embed_commands = settings.custom_commands["2"]

		command = command.lower()
		if len(output) == 1:
			output = output[0]

		if ctx.message.mentions or ctx.message.mention_everyone or ctx.message.role_mentions:
			return await ctx.send("Custom Commands cannot mention people/roles/everyone.")
		elif len(output) > 1800:
			return await ctx.send("The output is too long")
		elif command in self.bot.all_commands.keys() and command_type == "1":
			return await ctx.send("This is already the name of a built in command.")
		elif command in no_prefix_commands or command in prefix_commands or command in embed_commands:
			return await ctx.send("Custom Command already exists.")
		elif len(command.split(" ")) > 1 and command_type == "1":
			return await ctx.send("Custom commands with a prefix can only be one word with no spaces.")

		settings.custom_commands[command_type][command] = output
		settings.update(settings.custom_commands, "custom_commands")
		return await ctx.send("{} has been added with the output: '{}'".format(command, output))

	@custom.command()
	async def edit(self, ctx, command, edit):
		""""Edits an existing custom command."""
		settings = roxbot.guild_settings.get(ctx.guild)
		zero = settings.custom_commands["0"]
		one = settings.custom_commands["1"]

		if ctx.message.mentions or ctx.message.mention_everyone or ctx.message.role_mentions:
			return await ctx.send("Custom Commands cannot mention people/roles/everyone.")

		if command in zero:
			settings.custom_commands["0"][command] = edit
			settings.update(settings.custom_commands, "custom_commands")
			return await ctx.send("Edit made. {} now outputs {}".format(command, edit))
		elif command in one:
			settings.custom_commands["1"][command] = edit
			settings.update(settings.custom_commands, "custom_commands")
			return await ctx.send("Edit made. {} now outputs {}".format(command, edit))
		else:
			return await ctx.send("That Custom Command doesn't exist.")

	@custom.command(pass_context=True)
	async def remove(self, ctx, command):
		""""Removes a custom command."""
		settings = roxbot.guild_settings.get(ctx.guild)
		command = command.lower()
		if command in settings.custom_commands["1"]:
			settings.custom_commands["1"].pop(command)
			settings.update(settings.custom_commands, "custom_commands")
			return await ctx.send("Removed {} custom command".format(command))
		elif command in settings.custom_commands["0"]:
			settings.custom_commands["0"].pop(command)
			settings.update(settings.custom_commands, "custom_commands")
			return await ctx.send("Removed {} custom command".format(command))
		else:
			return await ctx.send("Custom Command doesn't exist.")

	@custom.command(pass_context=True)
	async def list(self, ctx, debug="0"):
		""""Lists all custom commands for this server."""
		if debug != "0" and debug != "1":
			debug = "0"
		settings = roxbot.guild_settings.get(ctx.guild)
		cc = settings.custom_commands
		listzero = ""
		listone = ""

		for command in cc["0"]:
			if debug == "1":
				command += " - {}".format(cc["0"][command])
			listzero = listzero + "- " + command + "\n"
		for command in cc["1"]:
			if debug == "1":
				command += " - {}".format(cc["1"][command])
			listone = listone + "- " + command + "\n"
		if not listone:
			listone = "There are no commands setup.\n"
		if not listzero:
			listzero = "There are no commands setup.\n"

		# TODO: Sort out a way to shorten this if it goes over 2000 characters.
		
		em = discord.Embed(title="Here is the list of Custom Commands", color=roxbot.EmbedColours.pink)
		em.add_field(name="Commands that require Prefix:", value=listone, inline=False)
		em.add_field(name="Commands that don't:", value=listzero, inline=False)
		return await ctx.send(embed=em)


def setup(bot_client):
	bot_client.add_cog(CustomCommands(bot_client))
