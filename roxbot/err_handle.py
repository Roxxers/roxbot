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

	async def on_command_error(self, ctx, error):
		owner = self.bot.get_user(self.bot.owner_id)
		if self.dev:
			raise error
		else:
			# UserError warning section

			user_errors = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments)

			if isinstance(error, user_errors):
				embed = discord.Embed(colour=roxbot.EmbedColours.orange)
				if isinstance(error, commands.MissingRequiredArgument):
					embed.description = "Required argument missing. {}".format(error.args[0])
				elif isinstance(error, commands.BadArgument):
					embed.description = "Bad Argument given. {}".format(error.args[0])
				elif isinstance(error, commands.TooManyArguments):
					embed.description = "Too many arguments given."
				elif isinstance(error, roxbot.UserError):
					embed.description = error.args[0]
				elif isinstance(error, roxbot.CogSettingDisabled):
					embed.description = "The following is not enabled on this server: {}".format(error.args[0])
				return await ctx.send(embed=embed)

			# ActualErrorHandling
			embed = discord.Embed()
			if isinstance(error, commands.NoPrivateMessage):
				embed.description = "This command cannot be used in private messages."
			elif isinstance(error, commands.DisabledCommand):
				embed.description = "This command is disabled."
			elif isinstance(error, commands.CommandNotFound):
				try:
					# Sadly this is the only part that makes a cog not modular. I have tried my best though to make it usable without the cog.
					cc = guild_settings.get(ctx.guild)["custom_commands"]
					is_custom_command = bool(ctx.invoked_with in cc["1"] or ctx.invoked_with in cc["2"])
					is_emoticon_face = bool(any(x in string.punctuation for x in ctx.message.content.strip(ctx.prefix)[0]))
					is_too_short = bool(len(ctx.message.content) <= 2)
					if is_custom_command or is_emoticon_face or is_too_short:
						embed = None
					else:
						embed.description = "That Command doesn't exist."
				except KeyError:
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
					embed.add_field(name='User', value=ctx.author)
					embed.add_field(name='Message', value=ctx.message.content)
					embed.timestamp = datetime.datetime.utcnow()
			elif isinstance(error, commands.CommandError):
				embed.description = "Command Error. {}".format(error.args[0])
			else:
				raise error
			if embed:
				embed.colour = roxbot.EmbedColours.dark_red
				await ctx.send(embed=embed)


def setup(bot_client):
	bot_client.add_cog(ErrHandle(bot_client))
