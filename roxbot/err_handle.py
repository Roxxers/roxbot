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


import string
import datetime
import traceback
import youtube_dl

import discord
from discord.ext import commands

import roxbot
from roxbot import guild_settings


class ErrHandle:
	def __init__(self, bot_client):
		self.bot = bot_client
		self.dev = roxbot.dev_mode

	async def on_error(self, event):
		if self.dev:
			traceback.print_exc()
		else:
			embed = discord.Embed(title="Roxbot Error", colour=roxbot.EmbedColours.red)
			embed.add_field(name='Event', value=event)
			embed.description = '```py\n{}\n```'.format(traceback.format_exc())
			embed.timestamp = datetime.datetime.utcnow()
			await self.bot.get_user(self.bot.owner_id).send(embed=embed)

	async def on_command_error(self, ctx, error):
		owner = self.bot.get_user(self.bot.owner_id)
		if self.dev:
			raise error
		else:
			embed = discord.Embed()
			if isinstance(error, commands.NoPrivateMessage):
				embed.description = "This command cannot be used in private messages."
			elif isinstance(error, commands.DisabledCommand):
				embed.description = "This command is disabled."
			elif isinstance(error, commands.MissingRequiredArgument):
				embed.description = "Required argument missing. {}".format(error.args[0])
			elif isinstance(error, commands.BadArgument):
				embed.description = "Bad Argument given. {}".format(error.args[0])
			elif isinstance(error, commands.TooManyArguments):
				embed.description = "Too many arguments given."
			elif isinstance(error, commands.CommandNotFound):
				cc = guild_settings.get(ctx.guild)["custom_commands"]
				if ctx.invoked_with in cc["1"] or ctx.invoked_with in cc["2"]:
					embed = None
				elif len(ctx.message.content) <= 2:
					embed = None
				elif any(x in string.punctuation for x in ctx.message.content.strip(ctx.prefix)[0]):
					# Should avoid punctuation emoticons. Checks all of the command for punctuation in the string.
					embed = None
				else:
					embed.description = "That Command doesn't exist."
			elif isinstance(error, commands.BotMissingPermissions):
				embed.description = "{}".format(error.args[0].replace("Bot", "roxbot"))
			elif isinstance(error, commands.MissingPermissions):
				embed.description = "{}".format(error.args[0])
			elif isinstance(error, commands.NotOwner):
				embed.description = "You do not have permission to do this. You are not Roxie!"
			elif isinstance(error, commands.CommandOnCooldown):
				embed.description = "This command is on cooldown, please wait {:.2f} seconds before trying again.".format(error.retry_after)
			elif isinstance(error, commands.CheckFailure):
				embed.description = "You do not have permission to do this. Back off, thot!"

			elif isinstance(error, commands.CommandInvokeError):
				# YOUTUBE_DL ERROR HANDLING
				if isinstance(error.original, youtube_dl.utils.GeoRestrictedError):
					embed.description = "Video is GeoRestricted. Cannot download."
				elif isinstance(error.original, youtube_dl.utils.DownloadError):
					embed.description = "Video could not be downloaded: {}".format(error.original.exc_info[1])

				# Final catches for errors undocumented.
				else:
					embed = discord.Embed(title='Command Error', colour=roxbot.EmbedColours.dark_red)
					embed.description = str(error)
					embed.add_field(name='Server', value=ctx.guild)
					try:
						embed.add_field(name='Channel', value=ctx.channel.mention)
					except AttributeError:
						embed.add_field(name='Channel', value=ctx.channel.id)
					embed.add_field(name='User', value=ctx.author)
					embed.add_field(name='Message', value=ctx.message.content)
					embed.timestamp = datetime.datetime.utcnow()
			elif isinstance(error, commands.CommandError):
				embed.description = "Command Error. {}".format(error.args[0])
			else:
				embed = discord.Embed(
					description="Placeholder embed. If you see this please message {}.".format(str(owner)))
			if embed:
				embed.colour = roxbot.EmbedColours.dark_red
				await ctx.send(embed=embed)


def setup(bot_client):
	bot_client.add_cog(ErrHandle(bot_client))
