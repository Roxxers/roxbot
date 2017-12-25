import checks
import datetime
import requests
import load_config
from discord.ext.commands import bot
from config.server_config import ServerConfig


class GaySoundsShitposting():
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	@checks.is_gss()
	@bot.command(pass_context=True)
	async def selfieperms(self, ctx):
		"""Requests the selfie perm role."""

		member = ctx.message.author
		server = ctx.message.server
		set_role = "394939389823811584"
		role_obj = None
		required_score = int(self.servers[server.id]["gss"]["required_score"])
		days = int(self.servers[server.id]["gss"]["required_days"])
		logging = self.servers[server.id]["gss"]["log_channel"]

		for role in server.roles:
			if role.id == set_role:
				role_obj = role

		if role_obj in member.roles:
			return await self.bot.say("You already have the {} role.".format(role_obj.name))

		base = "https://api.tatsumaki.xyz/"
		url = base + "guilds/" + server.id + "/members/" + member.id + "/stats"

		r = requests.get(url,headers={"Authorization":load_config.tat_token})
		data = r.json()

		time = datetime.datetime.now() - ctx.message.author.joined_at

		if time > datetime.timedelta(days=days) and int(data["score"]) >= required_score:
			await self.bot.add_roles(member, role_obj)
			await self.bot.say("You have now got the {} role".format(role_obj.name))
			if logging:
				return await self.bot.send_message(self.bot.get_channel(logging), content="{} has requested the {} role.".format(member.mention, role_obj.name))
		else:
			return await self.bot.say(
				"You do not meet the requirements for this role. You need at least {} score with <@!172002275412279296> and to have been in the server for {} days.".format(required_score, days)
			)

	@checks.is_gss()
	@bot.command(pass_context=True)
	async def nsfwperms(self, ctx):
		"""Requests the NSFW Image Perm role."""

		member = ctx.message.author
		server = ctx.message.server
		set_role = "394941004043649036"
		role_obj = None
		required_score = int(self.servers[server.id]["gss"]["required_score"])
		days = int(self.servers[server.id]["gss"]["required_days"])
		logging = self.servers[server.id]["gss"]["log_channel"]

		for role in server.roles:
			if role.id == set_role:
				role_obj = role

		if role_obj in member.roles:
			return await self.bot.say("You already have the {} role.".format(role_obj.name))

		base = "https://api.tatsumaki.xyz/"
		url = base + "guilds/" + server.id + "/members/" + member.id + "/stats"

		r = requests.get(url,headers={"Authorization":load_config.tat_token})
		data = r.json()

		time = datetime.datetime.now() - ctx.message.author.joined_at

		if time > datetime.timedelta(days=days) and int(data["score"]) >= required_score:
			await self.bot.add_roles(member, role_obj)
			await self.bot.say("You have now got the {} role".format(role_obj.name))
			if logging:
				return await self.bot.send_message(self.bot.get_channel(logging), content="{} has requested the {} role.".format(member.mention, role_obj.name))
		else:
			return await self.bot.say(
				"You do not meet the requirements for this role. You need at least {} score with <@!172002275412279296> and to have been in the server for {} days.".format(required_score, days)
			)

def setup(Bot):
	Bot.add_cog(GaySoundsShitposting(Bot))
