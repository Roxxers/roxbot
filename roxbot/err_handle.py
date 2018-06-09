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
import discord
import datetime
import traceback
from discord.ext import commands
import roxbot
from roxbot import guild_settings


class ErrHandle:
	def __init__(self, bot_client):
		self.bot = bot_client
		self.dev = False  # For debugging

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
		elif isinstance(error, commands.CommandInvokeError):
			embed = discord.Embed(title='Command Error', colour=roxbot.EmbedColours.dark_red)
			embed.description = str(error)
			embed.add_field(name='Server', value=ctx.guild)
			embed.add_field(name='Channel', value=ctx.channel.mention)
			embed.add_field(name='User', value=ctx.author)
			embed.add_field(name='Message', value=ctx.message.content)
			embed.timestamp = datetime.datetime.utcnow()
			await ctx.send(embed=embed)
		else:
			if isinstance(error, commands.NoPrivateMessage):
				embed = discord.Embed(description="This command cannot be used in private messages.")
			elif isinstance(error, commands.DisabledCommand):
				embed = discord.Embed(description="This command is disabled.")
			elif isinstance(error, commands.MissingRequiredArgument):
				embed = discord.Embed(description="Required argument missing. {}".format(error.args[0]))
			elif isinstance(error, commands.BadArgument):
				embed = discord.Embed(description="Bad Argument given. {}".format(error.args[0]))
			elif isinstance(error, commands.TooManyArguments):
				embed = discord.Embed(description="Too many arguments given.")
			elif isinstance(error, commands.CommandNotFound):
				cc = guild_settings.get(ctx.guild).custom_commands
				if ctx.invoked_with in cc["1"]:
					embed = None
				elif len(ctx.message.content) <= 2:
					embed = None
				elif any(x in string.punctuation for x in ctx.message.content.strip(ctx.prefix)[0]):
					# Should avoid punctuation emoticons. Checks all of the command for punctuation in the string.
					embed = None
				else:
					embed = discord.Embed(description="That Command doesn't exist.")
			elif isinstance(error, commands.BotMissingPermissions):
				embed = discord.Embed(description="{}".format(error.args[0].replace("Bot", "roxbot")))
			elif isinstance(error, commands.MissingPermissions):
				embed = discord.Embed(description="{}".format(error.args[0]))
			elif isinstance(error, commands.NotOwner):
				embed = discord.Embed(description="You do not have permission to do this. You are not Roxie!")
			elif isinstance(error, commands.CommandOnCooldown):
				embed = discord.Embed(description="This command is on cooldown, please wait {:.2f} seconds before trying again.".format(error.retry_after))
			elif isinstance(error, commands.CheckFailure):
				embed = discord.Embed(description="You do not have permission to do this. Back off, thot!")
			elif isinstance(error, commands.CommandError):
				embed = discord.Embed(description="Command Error. {}".format(error.args[0]))
			else:
				embed = discord.Embed(
					description="Placeholder embed. If you see this please message {}.".format(str(owner)))
			if embed:
				embed.colour = roxbot.EmbedColours.dark_red
				await ctx.send(embed=embed, delete_after=8)


def setup(bot_client):
	bot_client.add_cog(ErrHandle(bot_client))
