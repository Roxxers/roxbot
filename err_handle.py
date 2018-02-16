import traceback
import datetime
import load_config
import discord
from config.server_config import ServerConfig
from discord.ext import commands


class ErrHandle():
	def __init__(self, Bot):
		self.bot = Bot
		self.dev = True  # For debugging
		self.slow_mode = False
		self.slow_mode_channels = {}
		self.users = {}
		self.con = ServerConfig()
		self.servers = self.con.servers

	async def on_error(self, event, *args, **kwargs):
		if self.dev:
			traceback.print_exc()
		else:
			embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c) #Red
			embed.add_field(name='Event', value=event)
			embed.description = '```py\n%s\n```' % traceback.format_exc()
			embed.timestamp = datetime.datetime.utcnow()
			try:
				await self.bot.send_message(self.bot.owner_id, embed=embed)
			except:
				pass


	async def on_command_error(self, error, ctx):
		if isinstance(error, commands.NoPrivateMessage):
			await self.bot.send_message(ctx.message.author, "This command cannot be used in private messages.")
		elif isinstance(error, commands.DisabledCommand):
			await self.bot.send_message(ctx.message.channel, content="This command is disabled.")
		elif isinstance(error, commands.CheckFailure):
			await self.bot.send_message(ctx.message.channel, content="You do not have permission to do this. Back off, thot!")
		elif isinstance(error, KeyError):
			await self.bot.send_message(ctx.message.channel, content="Belgh")
		elif isinstance(error, commands.CommandInvokeError):
			if self.dev:
				raise error
			else:
				embed = discord.Embed(title=':x: Command Error', colour=0x992d22) #Dark Red
				embed.add_field(name='Error', value=str(error))
				embed.add_field(name='Server', value=ctx.message.server)
				embed.add_field(name='Channel', value=ctx.message.channel)
				embed.add_field(name='User', value=ctx.message.author)
				embed.add_field(name='Message', value=ctx.message.content)
				embed.timestamp = datetime.datetime.utcnow()
				try:
					await self.bot.send_message(await self.bot.get_user_info(load_config.owner), embed=embed)
				except:
					raise error
		else:
			if self.dev:
				raise error

def setup(Bot):
	Bot.add_cog(ErrHandle(Bot))