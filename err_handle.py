import traceback
import datetime
import discord
from discord.ext import commands
from config.server_config import ServerConfig

class ErrHandle:
	def __init__(self, bot_client):
		self.bot = bot_client
		self.dev = False  # For debugging
		self.servers = ServerConfig().servers

	async def on_error(self, event, *args, **kwargs):
		if self.dev:
			traceback.print_exc()
		else:
			embed = discord.Embed(title="Roxbot Error", colour=0xe74c3c) # Red
			embed.add_field(name='Event', value=event)
			embed.description = '```py\n{}\n```'.format(traceback.format_exc())
			embed.timestamp = datetime.datetime.utcnow()
			await self.owner.send(embed=embed)

	async def on_command_error(self, ctx, error):
		self.owner = self.bot.get_user(self.bot.owner_id)
		err_colour = 0x992d22
		if self.dev:
			raise error
		elif isinstance(error, commands.CommandInvokeError):
			embed = discord.Embed(title='Command Error', colour=err_colour)
			embed.description = str(error)
			embed.add_field(name='Server', value=ctx.guild)
			embed.add_field(name='Channel', value=ctx.channel.mention)
			embed.add_field(name='User', value=ctx.author)
			embed.add_field(name='Message', value=ctx.message.content)
			embed.timestamp = datetime.datetime.utcnow()
			await self.owner.send(embed=embed)
		else:
			if isinstance(error, commands.NoPrivateMessage):
				embed = discord.Embed(description="This command cannot be used in private messages.")
			elif isinstance(error, commands.DisabledCommand):
				embed = discord.Embed(description="This command is disabled.")
			elif isinstance(error, commands.CheckFailure):
				embed = discord.Embed(description="You do not have permission to do this. Back off, thot!")
			elif isinstance(error, commands.MissingRequiredArgument):
				embed = discord.Embed(description="Argument missing.")
			elif isinstance(error, commands.BadArgument):
				embed = discord.Embed(description="Invalid Argument given. Please check arguments given.")
			elif isinstance(error, commands.TooManyArguments):
				embed = discord.Embed(description="Too many arguments given.")
			elif isinstance(error, commands.CommandNotFound):
				cc = self.servers[str(ctx.guild.id)]["custom_commands"]
				if ctx.invoked_with in cc["1"]:
					embed = None
				else:
					embed = discord.Embed(description="That Command doesn't exist.")
			elif isinstance(error, commands.BotMissingPermissions):
				embed = discord.Embed(description="I am missing the following permissions: {}".format(str(error.missing_perms).strip("[]")))
			elif isinstance(error, commands.MissingPermissions):
				embed = discord.Embed(description="You are missing the following permissions: {}".format(str(error.missing_perms).strip("[]")))
			elif isinstance(error, commands.NotOwner):
				embed = discord.Embed(description="You do not have permission to do this. You are not Roxie!")
			elif isinstance(error, commands.CommandOnCooldown):
				embed = discord.Embed(description="This command is on cooldown, please wait {} seconds before trying again.".format(error.retry_after))
			else:
				embed = discord.Embed(
					description="Placeholder embed. If you see this please message {}.".format(str(self.owner)))
			if embed:
				embed.colour = err_colour
				await ctx.send(embed=embed)


def setup(bot_client):
	bot_client.add_cog(ErrHandle(bot_client))
