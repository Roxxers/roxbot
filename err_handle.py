import traceback
import datetime
import load_config
import discord
from discord.ext import commands


class ErrHandle():
	def __init__(self, Bot):
		self.bot = Bot
		self.dev = True  # For debugging

	async def on_error(self, event, *args, **kwargs):
		if self.dev:
			traceback.print_exc()
		else:
			embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c) #Red
			embed.add_field(name='Event', value=event)
			embed.description = '```py\n{}\n```'.format(traceback.format_exc())
			embed.timestamp = datetime.datetime.utcnow()
			try:
				await self.bot.send_message(self.bot.owner_id, embed=embed)
			except:
				pass


	async def on_command_error(self, ctx, error):
		err_colour = 0x992d22
		if isinstance(error, commands.CommandInvokeError):
			if self.dev:
				raise error
			else:
				embed = discord.Embed(title=':x: Command Error', colour=err_colour) #Dark Red
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
			if isinstance(error, commands.NoPrivateMessage):
				embed = discord.Embed(description="This command cannot be used in private messages.", colour=err_colour)
				await ctx.send(embed=embed)
			elif isinstance(error, commands.DisabledCommand):
				embed = discord.Embed(description="This command is disabled.", colour=err_colour)
				await ctx.send(embed=embed)
			elif isinstance(error, commands.CheckFailure):
				embed = discord.Embed(description="You do not have permission to do this. Back off, thot!", colour=err_colour)
				await ctx.send(embed=embed)
			elif isinstance(error, commands.MissingRequiredArgument):
				embed = discord.Embed(description="This command cannot be used in private messages.", colour=err_colour)
			elif isinstance(error, commands.BadArgument):
				embed = discord.Embed(description="Invalid Argument given. Please check them.", colour=err_colour)
			else:
				embed = discord.Embed(
					description="Placeholder embed. If you see this please message {}.".format(self.bot.get_user(self.bot.owner_id)))
			await ctx.send(embed=embed)


def setup(Bot):
	Bot.add_cog(ErrHandle(Bot))