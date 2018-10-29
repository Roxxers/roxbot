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
import random
import discord
from discord.ext import commands

import roxbot


class Util():
	"""
	A cog that offers utility commands.
	"""
	def __init__(self, bot_client):
		self.bot = bot_client

	@commands.command()
	async def avatar(self, ctx, *, user: discord.User = None):
		"""
		Returns a mentioned users avatar
		Example:
		{command_prefix}avatar @RoxBot#4170
		{command_prefix}avatar RoxBot
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

	@commands.command()
	async def info(self, ctx, member: discord.Member = None):
		"""
		Gets info for a mentioned user
		Example:
		{command_prefix}info @RoxBot#4170
		{command_prefix}info RoxBot
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
		"""Returns info on the current guild(server)."""
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
		"""Displays the info on a role"""
		embed = discord.Embed(title="Role '{}'".format(role.name), colour=role.colour.value)
		embed.add_field(name="ID", value=role.id, inline=False)
		embed.add_field(name="Created at", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(discord.utils.snowflake_time(role.id)), inline=False)
		embed.add_field(name="Colour", value="#{}".format(str(hex(role.colour.value)).strip("0x")), inline=False)
		embed.add_field(name="Hoisted", value=str(role.hoist), inline=False)
		embed.add_field(name="Managed", value=str(role.managed), inline=False)
		return await ctx.send(embed=embed)

	@commands.command(enabled=False, hidden=True)
	async def upload(self, ctx):
		"""
		Uploads selected file to the host, thanks to the fact that
		every pomf.se based site has pretty much the same architecture.
		"""
		sites = [
			"https://comfy.moe/",
			"https://mixtape.moe/",
			"https://doko.moe/",
			##"https://pomfe.co/",
			##"https://pomf.space/",
			"https://vidga.me/",
			"https://pomf.pyonpyon.moe/"
		]  # List of pomf clone sites and upload limits
		if ctx.message.attachments:
			# Site choice, shouldn't need an upload size check since max upload for discord atm is 50MB
			site = random.choice(sites)
			urls = []

			print(site)
			for attachment in ctx.message.attachments:
				name = attachment.url.split("/")[-1]
				# Download File
				await roxbot.http.download_file(attachment.url, name)

				response = await roxbot.http.upload_file(site+"upload.php", name)
				file_name_1 = response["files"][0]["url"].replace("\\", "")
				urls.append(file_name_1)
				os.remove(name)
			msg = "".join(urls)
			return await ctx.send(msg)
		else:
			return await ctx.send("Send me stuff to upload.")

	@upload.error
	async def upload_err(self, ctx):
		return await ctx.send("File couldn't be uploaded.")

	@commands.command(aliases=["emoji"])
	async def emote(self, ctx, emote: roxbot.converters.Emoji):
		"""
		Displays info on the given emote.
		Usage:
			;emote [emote]
		"""
		try:
			if isinstance(emote, str):
				emote = emote.strip("<>").split(":")
				if emote[0] == "a":
					emoji_id = emote[2]
				else:
					emoji_id = emote[2]
				url = "https://cdn.discordapp.com/emojis/{}".format(emoji_id)
				return await ctx.send(url)
			else:
				em = discord.Embed(title=emote.name, colour=roxbot.EmbedColours.blue)
				em.add_field(name="ID", value=str(emote.id), inline=False)
				if isinstance(emote, discord.Emoji):
					em.add_field(name="Guild", value=str(emote.guild), inline=False)
					em.add_field(name="Created At", value=roxbot.datetime_formatting.format(emote.created_at), inline=False)
				em.set_image(url=emote.url)
				return await ctx.send(embed=em)
		except IndexError:
			return await ctx.send("This command only supports custom emojis at the moment. Sorry.")

	@commands.command()
	async def invite(self, ctx):
		"""Returns an invite link to invite the bot to your server."""
		link = discord.utils.oauth_url(self.bot.user.id, discord.Permissions.all_channel())
		return await ctx.send("Invite me to your server! <{}>".format(link))

	@commands.command()
	@commands.is_owner()
	async def echo(self, ctx, channel: discord.TextChannel, *, message: str):
		"""Repeats after you, Roxie."""
		await channel.send(message)
		return await ctx.send(":point_left:")


def setup(bot_client):
	bot_client.add_cog(Util(bot_client))
