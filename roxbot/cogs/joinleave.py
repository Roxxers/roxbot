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
					"member-role": "",
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

		channel = self.bot.get_channel(settings["greets"]["welcome-channel"])
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
			channel = self.bot.get_channel(channel)
			return await channel.send(embed=discord.Embed(
				description="{}#{} has left or been beaned.".format(member.name, member.discriminator), colour=roxbot.EmbedColours.pink))


def setup(Bot):
	Bot.add_cog(JoinLeave(Bot))
