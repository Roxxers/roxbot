import os
import json
import random
import aiohttp
import discord
import requests
from discord.ext import commands
from discord.ext.commands import bot

class Util():
	"""
	A cog that offers utility commands.
	"""
	def __init__(self, bot_client):
		self.bot = bot_client

	@bot.command()
	async def avatar(self, ctx, *,user: discord.User = None):
		"""
		Returns a mentioned users avatar
		Example:
		{command_prefix}avatar @RoxBot#4170
		{command_prefix}avatar RoxBot
		"""
		if not user:
			user = ctx.author

		url = user.avatar_url
		if url.split(".")[-1] == "gif":
			avaimg = 'avaimg.gif'
		else:
			avaimg = 'avaimg.webp'

		async with aiohttp.ClientSession() as session:
			async with session.get(url) as img:
				with open(avaimg, 'wb') as f:
					f.write(await img.read())
		await ctx.send(file=discord.File(avaimg))
		os.remove(avaimg)

	@bot.command()
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
	@bot.command(aliases=["server"])
	async def guild(self, ctx):
		"""Returns info on the current guild(server)."""
		guild = ctx.guild
		guild_icon_url = "https://cdn.discordapp.com/icons/{}/{}.png".format(guild.id, guild.icon)
		guild_splash_url = "https:/cdn.discordapp.com/splashes/{}/{}.png".format(guild.id, guild.splash)
		embed = discord.Embed(title=guild.name, colour=guild.me.colour.value)
		embed.set_thumbnail(url=guild_icon_url)
		embed.add_field(name="ID", value=guild.id, inline=False)
		embed.add_field(name="Created at", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(guild.created_at, inline=False))
		embed.add_field(name="Voice Region", value=guild.region, inline=False)
		embed.add_field(name="AFK Timeout", value="{} Minutes".format(guild.afk_timeout/60), inline=False)
		if guild.afk_channel:
			embed.add_field(name="AFK Channel", value=guild.afk_channel, inline=False)

		embed.add_field(name="Owner", value="{} ({})".format(self.bot.get_user(guild.owner_id), guild.owner_id), inline=False)
		embed.add_field(name="Verification Level", value=guild.verification_level, inline=False)
		embed.add_field(name="Explicit Content Filtering", value=guild.explicit_content_filter, inline=False)
		embed.add_field(name="Roles [{}]".format(len(guild.roles)), value="For all roles, use `{}guild roles`.", inline=False)
		embed.add_field(name="Emotes [{}]".format(len(guild.emojis)), value="For all emotes, use `{}guild emotes`.".format(self.bot.command_prefix), inline=False)
		embed.add_field(name="Channels [{}]".format(len(guild.channels)), value="{} Channel Categories\n{} Text Channels\n{} Voice Channels".format(len(guild.categories), len(guild.text_channels), len(guild.voice_channels)))

		if guild.features:
			embed.add_field(name="Extra Features", value=guild.features)
		if guild.splash:
			embed.set_image(url=guild_splash_url)

		return await ctx.send(embed=embed)

	@commands.guild_only()
	@bot.command()
	async def role(self, ctx, *, role: discord.Role):
		"""Displays the info on a role"""
		embed = discord.Embed(title="Role '{}'".format(role.name), colour=role.colour.value)
		embed.add_field(name="ID", value=role.id, inline=False)
		embed.add_field(name="Created at", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(discord.utils.snowflake_time(role.id)), inline=False)
		embed.add_field(name="Colour", value="#{}".format(str(hex(role.colour.value)).strip("0x")), inline=False)
		embed.add_field(name="Hoisted", value=str(role.hoist), inline=False)
		embed.add_field(name="Managed", value=str(role.managed), inline=False)
		return await ctx.send(embed=embed)

	@bot.command()
	async def upload(self, ctx):
		"""
		Uploads selected file to the host, thanks to the fact that
		every pomf.se based site has pretty much the same architecture.
		"""
		sites = [
			"https://comfy.moe/",
			"https://safe.moe/api/",
			"http://up.che.moe/",
			"https://mixtape.moe/",
			"https://pomf.cat/",
			"https://sugoi.vidyagam.es/",
			"https://doko.moe/",
			"https://pomfe.co/",
			"https://pomf.space/",
			"https://vidga.me/",
			"https://pomf.pyonpyon.moe/"
		] # List of pomf clone sites and upload limits
		if ctx.message.attachments:
			# Site choice, shouldn't need an upload size check since max upload for discord atm is 50MB
			site = random.choice(sites)
			urls = []
			for attachment in ctx.message.attachments:
				name = attachment['url'].split("/")[-1]
				# Download File
				with aiohttp.ClientSession() as session:
					async with session.get(attachment['url']) as img:
						with open(name, 'wb') as f:
							f.write(await img.read())
				# Upload file
				with open(name, 'rb') as f:
					answer = requests.post(url=site+"upload.php",files={'files[]': f.read()})
					response = json.loads(answer.text)
					file_name_1 = response["files"][0]["url"].replace("\\", "")
				urls.append(file_name_1)
				os.remove(name)
			msg = "".join(urls)
			return await ctx.send(msg)
		else:
			return await ctx.send("Send me stuff to upload.")

	@upload.error
	async def upload_err(self, ctx, error):
		return await ctx.send("File couldn't be uploaded. {}".format(error))

	@bot.command(aliases=["emoji"])
	async def emote(self, ctx, emote):
		"""
		Uploads the emote given. Useful for downloading emotes.
		Usage:
			;emote [emote]
		"""
		emote = emote.strip("<>").split(":")
		if emote[0] == "a":
			imgname = "emote.gif"
			emoji_id = emote[2]
		else:
			imgname = "emote.png"
			emoji_id = emote[2]
		url = "https://cdn.discordapp.com/emojis/{}".format(emoji_id)

		async with aiohttp.ClientSession() as session:
			async with session.get(url) as img:
				with open(imgname, 'wb') as f:
					f.write(await img.read())
		await ctx.send(file=discord.File(imgname))
		os.remove(imgname)

	@bot.command(hidden=True)
	async def inviteme(self, ctx):
		"""Returns an invite link to invite the bot to your server."""
		link = discord.utils.oauth_url(self.bot.user.id, discord.Permissions.all_channel())
		return await ctx.send("WARNING: This is only for Roxie to use atm. Here is a link to invite me to your server! <{}>".format(link))

	@bot.command()
	@commands.is_owner()
	async def echo(self, ctx, channel: discord.TextChannel, *, message: str):
		await channel.send(message)
		return await ctx.send(":point_left:")


def setup(bot_client):
	bot_client.add_cog(Util(bot_client))
