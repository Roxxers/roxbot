import discord
from Roxbot import guild_settings


class JoinLeave():
	def __init__(self, Bot):
		self.bot = Bot

	async def on_member_join(self, member):
		"""
		Greets users when they join a server.
		"""
		settings = guild_settings.get(member.guild)
		if not settings.greets["enabled"]:
			return

		if settings.greets["custom-message"]:
			message = settings.greets["custom-message"]
		else:
			message = settings.greets["default-message"]
		em = discord.Embed(
			title="Welcome to {}!".format(member.guild),
			description='Hey {}! Welcome to **{}**! {}'.format(member.mention, member.guild, message),
			colour=0xDEADBF)
		em.set_thumbnail(url=member.avatar_url)

		channel = self.bot.get_channel(settings.greets["welcome-channel"])
		return await channel.send(embed=em)

	async def on_member_remove(self, member):
		"""
		The same but the opposite
		"""
		settings = guild_settings.get(member.guild)
		channel = settings.goodbyes["goodbye-channel"]
		if not settings.goodbyes["enabled"]:
			return
		else:
			channel = self.bot.get_channel(channel)
			return await channel.send(embed=discord.Embed(
				description="{}#{} has left or been beaned.".format(member.name, member.discriminator), colour=0xDEADBF))


def setup(Bot):
	Bot.add_cog(JoinLeave(Bot))
