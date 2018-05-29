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
from roxbot import guild_settings, EmbedColours


async def log(guild, channel, command_name, **kwargs):
	logging = guild_settings.get(guild).logging
	if logging["enabled"]:
		embed = discord.Embed(title="{} command logging".format(command_name), colour=EmbedColours.pink)
		for key, value in kwargs.items():
			embed.add_field(name=key, value=value)
		return await channel.send(embed=embed)


class Logging:
	def __init__(self, bot_client):
		self.bot = bot_client

	async def on_member_join(self, member):
		logging = guild_settings.get(member.guild).logging
		if logging["enabled"]:
			channel = self.bot.get_channel(logging["channel"])
			embed = discord.Embed(title="{} joined the server".format(member), colour=EmbedColours.pink)
			embed.add_field(name="ID", value=member.id)
			embed.add_field(name="Mention", value=member.mention)
			embed.add_field(name="Date Account Created", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(member.created_at))
			embed.add_field(name="Date Joined", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(member.joined_at))
			embed.set_thumbnail(url=member.avatar_url)
			return await channel.send(embed=embed)

	async def on_member_remove(self, member):
		# TODO: Add some way of detecting whether a user left/was kicked or was banned.
		logging = guild_settings.get(member.guild).logging
		if logging["enabled"]:
			channel = self.bot.get_channel(logging["channel"])
			embed = discord.Embed(description="{} left the server".format(member), colour=EmbedColours.pink)
			return await channel.send(embed=embed)


def setup(bot_client):
	bot_client.add_cog(Logging(bot_client))
