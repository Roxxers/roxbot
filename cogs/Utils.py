import os
from asyncio import sleep
import aiohttp
import discord
from discord.ext.commands import bot

class Util():
	def __init__(self, Bot):
		self.bot = Bot

	@bot.command(pass_context=True)
	async def avatar(self, ctx, user: discord.User = None):
		if ctx.message.mentions:
			user = ctx.message.mentions[0]
		elif not user:
			user = ctx.message.author

		url = user.avatar_url
		avaimg = 'avaimg.webp'

		async with aiohttp.ClientSession() as session:
			async with session.get(url) as img:
				with open(avaimg, 'wb') as f:
					f.write(await img.read())

		return await self.bot.send_file(ctx.message.channel, avaimg)

	@bot.command(pass_context=True)
	async def info(self, ctx, member: discord.Member = None):
		if not member:
			member = ctx.message.author
		name_disc = member.name + "#" + member.discriminator
		if member.game:
			if member.game.type:
				game = member.game.name
				desc = "Streaming "
			else:
				game = member.game.name
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
		embed.add_field(name="Account Created", value="{:%a %d/%m/%Y %H:%M:%S} UTC".format(member.created_at), inline=True)
		embed.add_field(name="Joined Server", value="{:%a %d/%m/%Y %H:%M:%S} UTC".format(member.joined_at), inline=True)

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
	async def remindme(self, ctx, minutes: int, *kwargs):
		if not kwargs:
			msg = "I'm here to remind you of something. Idk what, but you told me to do this {} minutes ago ¯\_(ツ)_/¯".format(str(minutes))
		else:
			msg = "I was told to remind you this: **'{}'** {} minutes ago.".format(" ".join(kwargs),str(minutes))
		#secs = minutes * 60
		await sleep(minutes)
		return await self.bot.reply(msg)

def setup(Bot):
	Bot.add_cog(Util(Bot))