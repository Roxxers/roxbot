import discord
from Roxbot.settings import guild_settings
from Roxbot.load_config import embedcolour


async def log(guild, channel, command_name, **kwargs):
	logging = guild_settings.get(guild).logging
	if logging["enabled"]:
		embed = discord.Embed(title="{} command logging".format(command_name), colour=embedcolour)
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
			embed = discord.Embed(title="{} joined the server".format(member), colour=embedcolour)
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
			embed = discord.Embed(description="{} left the server".format(member), colour=embedcolour)
			return await channel.send(embed=embed)


def setup(bot_client):
	bot_client.add_cog(Logging(bot_client))
