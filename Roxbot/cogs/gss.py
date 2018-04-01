import datetime
import requests
from Roxbot import load_config
import discord
from discord.ext import commands
from discord.ext.commands import bot
from Roxbot.settings import guild_settings
from json import JSONDecodeError


def is_gss():
	return commands.check(lambda ctx: ctx.guild.id == 393764974444675073)

def is_not_nsfw_disabled():
	def predicate(ctx):
		role = discord.utils.get(ctx.guild.roles, id=397866388145831937)
		return role not in ctx.author.roles
	return commands.check(lambda ctx: predicate(ctx))

class GaySoundsShitposts():
	def __init__(self, bot_client):
		self.bot = bot_client
		self.acceptable_roles = (394939389823811584, 394941004043649036)

	def tatsumaki_api_call(self, member, guild):
		base = "https://api.tatsumaki.xyz/"
		url = base + "guilds/" + str(guild.id) + "/members/" + str(member.id) + "/stats"
		r = requests.get(url, headers={"Authorization": load_config.tat_token})
		try:
			return r.json()
		except JSONDecodeError:
			return False

	@bot.command(hidden=True)
	async def perms(self, ctx, *, role: discord.Role = None):
		"""Shell command to do the perm assigning. Only should be invoked by another command."""
		# Just in case some cunt looks at the source code and thinks they can give themselves Admin.
		if role.id not in self.acceptable_roles:
			print("lol no")
			return False
		settings = guild_settings.get(ctx.guild)
		member = ctx.author
		required_score = settings.gss["required_score"]
		days = int(settings.gss["required_days"])
		data = self.tatsumaki_api_call(member, ctx.guild)
		if not data:
			return await ctx.send("Tatsumaki API call returned nothing. Maybe the API is down?")

		if role in member.roles:
			await member.remove_roles(role, reason="Requested removal of {0.name}".format(role))
			return await ctx.send("You already had {0.name}. It has now been removed.".format(role))

		time = datetime.datetime.now() - ctx.author.joined_at

		if time > datetime.timedelta(days=days) and int(data["score"]) >= required_score:
			await member.add_roles(member, role, reason="Requested {0.name}".format(role))
			await ctx.send("You have now have the {0.name} role".format(role))
		else:
			return await ctx.send(
				"You do not meet the requirements for this role. You need at least {} score with <@!172002275412279296> and to have been in the server for {} days.".format(required_score, days)
			)

	@is_gss()
	@bot.command()
	async def selfieperms(self, ctx):
		"""Requests the selfie perm role."""
		role = 394939389823811584
		return await ctx.invoke(self.perms, role=role)

	@is_not_nsfw_disabled()
	@is_gss()
	@bot.command()
	async def nsfwperms(self, ctx):
		"""Requests the NSFW Image Perm role."""
		role = 394941004043649036
		return await ctx.invoke(self.perms, role=role)

def setup(bot_client):
	bot_client.add_cog(GaySoundsShitposts(bot_client))
