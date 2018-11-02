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


import os
import emoji

import discord
from discord.ext import commands

import roxbot


class Util:
	"""
	The Util cog is a cog filled with a number of utility commands to help more advanced users of Discord.
	"""
	def __init__(self, bot_client):
		self.bot = bot_client

	@commands.command()
	async def avatar(self, ctx, *, user: discord.User = None):
		"""
		Uploads a downloadable picture of an avatar. 

		Example:
			# Get my avatar
			;avatar
			# Get USER's avatar
			;avatar USER#0001
		"""
		if not user:
			user = ctx.author

		url = user.avatar_url_as(static_format="png")
		if url.split(".")[-1] == "gif":
			avaimg = '{0.name}.gif'.format(user)
		else:
			avaimg = '{0.name}.png'.format(user)

		await roxbot.http.download_file(url, avaimg)
		await ctx.send(file=discord.File(avaimg))
		os.remove(avaimg)

	@commands.command(aliases=["user"])
	async def info(self, ctx, member: discord.Member = None):
		"""
		Provides information (account creation date, ID, roles [if in a guild]) on your or another persons account.

		Example:
			# Get account information for yourself
			;info
			# Get account information for a user called USER
			;info @USER
		"""
		if not member:
			member = ctx.author
		if member.activity:
			if member.activity.type == discord.ActivityType.playing:
				activity = "Playing **{}**".format(member.activity.name)
			elif member.activity.type == discord.ActivityType.streaming:
				activity = "Streaming **{}**".format(member.activity.name)
			elif member.activity.type == discord.ActivityType.listening:
				activity = "Listening to **{} by {}**".format(member.activity.title, member.activity.artist)
			else:
				activity = ""
		else:
			activity = ""

		colour = member.colour.value
		avatar = member.avatar_url

		embed = discord.Embed(colour=colour, description=activity)
		embed.set_thumbnail(url=avatar)
		embed.set_author(name=str(member), icon_url=avatar)

		embed.add_field(name="ID", value=member.id)
		embed.add_field(name="Status", value=member.status)
		if member.nick:
			embed.add_field(name="Nickname", value=member.nick)
		embed.add_field(name="Account Created", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(member.created_at), inline=True)
		embed.add_field(name="Joined Server", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(member.joined_at), inline=True)

		roles = ""
		count = 0

		for role in member.roles:
			if role == ctx.guild.default_role:
				pass
			else:
				roles += role.name + ", "
				count += 1
		if not roles:
			roles = "None"
			count = 0
		embed.add_field(name="Roles [{}]".format(count), value=roles.strip(", "))
		return await ctx.send(embed=embed)

	@commands.guild_only()
	@commands.command(aliases=["server"])
	async def guild(self, ctx):
		"""Gives information (creation date, owner, ID) on the guild this command is executed in."""
		guild = ctx.guild
		guild_icon_url = "https://cdn.discordapp.com/icons/{}/{}.png".format(guild.id, guild.icon)
		guild_splash_url = "https:/cdn.discordapp.com/splashes/{}/{}.png".format(guild.id, guild.splash)
		embed = discord.Embed(title=guild.name, colour=guild.me.colour.value)
		embed.set_thumbnail(url=guild_icon_url)
		embed.add_field(name="ID", value=guild.id, inline=False)
		embed.add_field(name="Owner", value="{} ({})".format(self.bot.get_user(guild.owner_id), guild.owner_id), inline=False)
		embed.add_field(name="Created at", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(guild.created_at, inline=False))
		embed.add_field(name="Voice Region", value=guild.region, inline=False)
		embed.add_field(name="AFK Timeout", value="{} Minutes".format(guild.afk_timeout/60), inline=False)
		if guild.afk_channel:
			embed.add_field(name="AFK Channel", value=guild.afk_channel, inline=False)

		embed.add_field(name="Verification Level", value=guild.verification_level, inline=False)
		embed.add_field(name="Explicit Content Filtering", value=guild.explicit_content_filter, inline=False)
		embed.add_field(name="Members", value=guild.member_count)
		number_of_bots = 0
		for member in guild.members:
			if member.bot:
				number_of_bots += 1
		human_members = guild.member_count - number_of_bots
		embed.add_field(name="Human Members", value=human_members, inline=False)
		embed.add_field(name="Roles".format(), value=str(len(guild.roles)), inline=False)
		embed.add_field(name="Emotes".format(), value=str(len(guild.emojis)), inline=False)
		embed.add_field(name="Channels [{}]".format(len(guild.channels)), value="{} Channel Categories\n{} Text Channels\n{} Voice Channels".format(len(guild.categories), len(guild.text_channels), len(guild.voice_channels)))

		if guild.features:
			embed.add_field(name="Extra Features", value=guild.features, inline=False)
		if guild.splash:
			embed.set_image(url=guild_splash_url)

		return await ctx.send(embed=embed)

	@commands.guild_only()
	@commands.command()
	async def role(self, ctx, *, role: discord.Role):
		"""Gives information (creation date, colour, ID) on the role given. Can only work if the role is in the guild you execute this command in.
		Examples:
			# Get information on the role called Admin
			;role Admin
		"""
		embed = discord.Embed(title="Role '{}'".format(role.name), colour=role.colour.value)
		embed.add_field(name="ID", value=role.id, inline=False)
		embed.add_field(name="Created at", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(discord.utils.snowflake_time(role.id)), inline=False)
		embed.add_field(name="Colour", value="#{}".format(str(hex(role.colour.value)).strip("0x")), inline=False)
		embed.add_field(name="Hoisted", value=str(role.hoist), inline=False)
		embed.add_field(name="Managed", value=str(role.managed), inline=False)
		return await ctx.send(embed=embed)

	@commands.command(aliases=["emoji"])
	async def emote(self, ctx, emote):
		"""
		Displays infomation (creation date, guild, ID) and an easily downloadable version of the given custom emote.

		Example:
			# Get infomation of the emoji ":Kappa:"
			;emote :Kappa:
		"""
		try:  # If emote given is custom emote
			emote = await roxbot.converters.Emoji().convert(ctx, emote)
			em = discord.Embed(title=emote.name, colour=roxbot.EmbedColours.blue)
			em.add_field(name="ID", value=str(emote.id), inline=False)
			if isinstance(emote, discord.Emoji):
				em.add_field(name="Guild", value=str(emote.guild), inline=False)
				em.add_field(name="Created At", value=roxbot.datetime_formatting.format(emote.created_at), inline=False)
			em.set_image(url=emote.url)
			return await ctx.send(embed=em)
		except commands.errors.BadArgument:  # unicode emoji
			title = emoji.demojize(emote)
			if not emoji.EMOJI_UNICODE.get(title):
				raise commands.BadArgument("Could not convert input to either unicode emoji or Discord custom emote.")

			emojis = []
			for char in emote:
				emojis.append(hex(ord(char))[2:])

			if len(emojis) > 1:
				svg_url = "https://twemoji.maxcdn.com/2/svg/{0}-{1}.svg".format(*emojis)
				png_url = "https://twemoji.maxcdn.com/2/72x72/{0}-{1}.png".format(*emojis)
			else:
				svg_url = "https://twemoji.maxcdn.com/2/svg/{0}.svg".format(*emojis)
				png_url = "https://twemoji.maxcdn.com/2/72x72/{0}.png".format(*emojis)

			em = discord.Embed(title=title, colour=roxbot.EmbedColours.blue)
			em.description = "[SVG Link]({0})\n[PNG Link]({1})".format(svg_url, png_url)
			em.set_image(url=png_url)

			return await ctx.send(embed=em)


def setup(bot_client):
	bot_client.add_cog(Util(bot_client))
