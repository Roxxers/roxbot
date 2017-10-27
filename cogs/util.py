import os
import json
import checks
import random
import aiohttp
import discord
import requests
from discord.ext.commands import bot

class Util():
	"""
	A cog that offers utility commands.
	"""
	def __init__(self, Bot):
		self.bot = Bot

	@bot.command(pass_context=True)
	async def avatar(self, ctx, *,user: discord.User = None):
		"""
		Returns a mentioned users avatar
		Example:
		{command_prefix}avatar @RoxBot#4170
		{command_prefix}avatar RoxBot
		"""
		if not user:
			user = ctx.message.author

		url = user.avatar_url
		avaimg = 'avaimg.webp'

		async with aiohttp.ClientSession() as session:
			async with session.get(url) as img:
				with open(avaimg, 'wb') as f:
					f.write(await img.read())
		await self.bot.send_file(ctx.message.channel, avaimg)
		os.remove(avaimg)

	@bot.command(pass_context=True)
	async def info(self, ctx, member: discord.Member = None):
		"""
		Gets info for a mentioned user
		Example:
		{command_prefix}info @RoxBot#4170
		{command_prefix}info RoxBot
		"""
		if not member:
			member = ctx.message.author
		name_disc = member.name + "#" + member.discriminator
		if member.game:
			if member.game.type:
				game = "**" + member.game.name + "**"
				desc = "Streaming "
			else:
				game = "**" + member.game.name + "**"
				desc = "Playing "
		else:
			desc = ""
			game = ""

		colour = member.colour.value
		avatar = member.avatar_url

		embed = discord.Embed(colour=colour, description=desc+game)
		embed.set_thumbnail(url=avatar)
		embed.set_author(name=name_disc, icon_url=avatar)

		embed.add_field(name="ID", value=member.id)
		embed.add_field(name="Status", value=member.status)
		if member.nick:
			embed.add_field(name="Nickname", value=member.nick)
		embed.add_field(name="Account Created", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(member.created_at), inline=True)
		embed.add_field(name="Joined Server", value="{:%a %Y/%m/%d %H:%M:%S} UTC".format(member.joined_at), inline=True)

		roles = ""
		count = 0

		for role in member.roles:
			if role == ctx.message.server.default_role:
				pass
			else:
				roles += role.name + ", "
				count += 1
		embed.add_field(name="Roles [{}]".format(count), value=roles.strip(", "))
		return await self.bot.say(embed=embed)

	@bot.command(pass_context=True)
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

		await self.bot.send_typing(ctx.message.channel)
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
				try:
					with open(name, 'rb') as f:
						answer = requests.post(url=site+"upload.php",files={'files[]': f.read()})
						response = json.loads(answer.text)
						file_name_1 = response["files"][0]["url"].replace("\\", "")
					urls.append(file_name_1)
				except Exception as e:
					print(e)
					print(name + ' couldn\'t be uploaded to ' + site)
				os.remove(name)
			msg = "".join(urls)
			return await self.bot.say(msg)
		else:
			return await self.bot.say("Send me shit to upload nig")

	@bot.command(pass_context=True)
	async def emote(self, ctx, emote):
		"""
		Gets a url to the emote given. Useful for downloading emotes.
		"""
		emoteid = emote.split(":")[-1].strip("<>")
		url = "https://discordapp.com/api/emojis/{}.png".format(emoteid)
		return await self.bot.say(url)

	@bot.command(pass_context=True, hidden=True)
	@checks.is_bot_owner()
	async def echo(self, ctx, channel, *, message: str):
		if ctx.message.channel_mentions:
			for channel in ctx.message.channel_mentions:
				await self.bot.send_message(channel, content=message)
			return await self.bot.say(":point_left:")
		elif channel.isdigit():
			channel = ctx.message.server.get_channel(channel)
			await self.bot.send_message(channel, content=message)
			return await self.bot.say(":point_left:")
		else:
			return await self.bot.say("You did something wrong smh")

def setup(Bot):
	Bot.add_cog(Util(Bot))