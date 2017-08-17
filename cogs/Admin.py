import discord
from discord.ext.commands import bot
from asyncio import sleep

from config.config import Config


class Admin():
	def __init__(self, Bot):
		self.bot = Bot
		self.con = Config(Bot)
		self.serverconfig = self.con.serverconfig

	@bot.command(pass_context=True, enabled=False)
	"""Its broke atm"""
	async def mute(self, ctx, minutes: int, user: discord.User = None):
		admins = self.serverconfig[ctx.message.server.id]["mute"]["admin-role"]
		muterole = self.serverconfig[ctx.message.server.id]["mute"]["role"]
		for roles in ctx.message.author.roles:
			if not roles.id in admins:
				return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		seconds = minutes #* 60
		await self.bot.add_roles(user, muterole)
		await self.bot.send_message(user,
									content="You have been muted on {} for {} minutes. This means you have been given a role that blocks you from talking in more/all channels. If you have an issue please contact an admin.".format(
										ctx.message.server.name, minutes))
		await self.bot.say("{} has been muted for {} minutes.".format(user.mention, minutes))
		await sleep(seconds)
		await self.bot.remove_roles(user, muterole)
		return await self.bot.say("{} has been unmuted.".format(user.mention))





def setup(Bot):
	Bot.add_cog(Admin(Bot))
