import discord
from Roxbot.settings.guild_settings import ServerConfig


class JoinLeave():
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	async def on_member_join(self, member):
		"""
		Greets users when they join a server.
		"""
		self.con.load_config()
		if not self.servers[str(member.guild.id)]["greets"]["enabled"]:
			return

		if self.servers[str(member.guild.id)]["greets"]["custom-message"]:
			message = self.servers[str(member.guild.id)]["greets"]["custom-message"]
		else:
			message = self.servers[str(member.guild.id)]["greets"]["default-message"]
		em = discord.Embed(
			title="Welcome to {}!".format(member.guild),
			description='Hey {}! Welcome to **{}**! {}'.format(member.mention, member.guild, message),
			colour=0xDEADBF)
		em.set_thumbnail(url=member.avatar_url)

		channel = self.bot.get_channel(self.servers[str(member.guild.id)]["greets"]["welcome-channel"])
		return await channel.send(embed=em)

	async def on_member_remove(self, member):
		"""
		The same but the opposite
		"""
		self.con.load_config()
		channel = self.servers[str(member.guild.id)]["goodbyes"]["goodbye-channel"]
		if not self.servers[str(member.guild.id)]["goodbyes"]["enabled"]:
			return
		else:
			channel = self.bot.get_channel(channel)
			return await channel.send(embed=discord.Embed(
				description="{}#{} has left or been beaned.".format(member.name, member.discriminator), colour=0xDEADBF))


def setup(Bot):
	Bot.add_cog(JoinLeave(Bot))