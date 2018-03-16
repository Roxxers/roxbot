import datetime
import requests
import load_config
from discord import utils
from discord.ext import commands
from discord.ext.commands import bot
from config.server_config import ServerConfig


def is_gss():
	return commands.check(lambda ctx: ctx.guild.id == 393764974444675073)

def is_not_nsfw_disabled():
	def predicate(ctx):
		role = utils.get(ctx.guild.roles, id=397866388145831937)
		return role not in ctx.author.roles
	return commands.check(lambda ctx: predicate(ctx))

class GaySoundsShitposting():
	def __init__(self, bot_client):
		self.bot = bot_client
		self.con = ServerConfig()
		self.servers = self.con.servers
		self.guild = self.bot.get_guild(393764974444675073)
		print(self.guild)
		print(self.guild.id == 393764974444675073)
		self.nsfw_image_role = utils.get(self.guild.roles, id=394941004043649036)
		self.selfie_role = utils.get(self.guild.roles, id=394939389823811584)

	def tatsumaki_api_call(self, member):
		base = "https://api.tatsumaki.xyz/"
		url = base + "guilds/" + self.guild.id + "/members/" + member.id + "/stats"
		r = requests.get(url,headers={"Authorization":load_config.tat_token})
		return r.json()

	@is_gss()
	@bot.command(pass_context=True)
	async def selfieperms(self, ctx):
		"""Requests the selfie perm role."""
		member = ctx.author
		required_score = int(self.servers[self.guild.id]["gss"]["required_score"])
		days = int(self.servers[self.guild.id]["gss"]["required_days"])
		data = self.tatsumaki_api_call(member)

		if self.selfie_role in member.roles:
			await member.remove_roles(self.selfie_role, reason="Requested removal of Selfie Perms")
			return await ctx.send("You already had {}. It has now been removed.".format(self.selfie_role.name))

		time = datetime.datetime.now() - ctx.author.joined_at

		if time > datetime.timedelta(days=days) and int(data["score"]) >= required_score:
			await member.add_roles(member, self.selfie_role, reason="Requested Selfie perms")
			await ctx.send("You have now have the {} role".format(self.selfie_role.name))
		else:
			return await ctx.send(
				"You do not meet the requirements for this role. You need at least {} score with <@!172002275412279296> and to have been in the server for {} days.".format(required_score, days)
			)

	@is_not_nsfw_disabled()
	@is_gss()
	@bot.command(pass_context=True)
	async def nsfwperms(self, ctx):
		"""Requests the NSFW Image Perm role."""
		member = ctx.author
		required_score = int(self.servers[self.guild.id]["gss"]["required_score"])
		days = int(self.servers[self.guild.id]["gss"]["required_days"])
		data = self.tatsumaki_api_call(member)

		if self.nsfw_image_role in member.roles:
			await member.remove_roles(self.nsfw_image_role, reason="Requested removal of NSFW Perms")
			return await ctx.send("You already had {}. It has now been removed.".format(self.nsfw_image_role.name))

		time = datetime.datetime.now() - ctx.author.joined_at

		if time > datetime.timedelta(days=days) and int(data["score"]) >= required_score:
			await member.add_roles(self.nsfw_image_role, reason="Requested NSFW perms")
			await ctx.send("You have now have the {} role".format(self.nsfw_image_role.name))
		else:
			return await ctx.send(
				"You do not meet the requirements for this role. You need at least {} score with <@!172002275412279296> and to have been in the server for {} days.".format(required_score, days)
			)

def setup(bot_client):
	bot_client.add_cog(GaySoundsShitposting(bot_client))
