from discord.ext.commands import bot
from discord.ext.commands import group
from config.server_config import ServerConfig


class CustomCommands():
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	@group(pass_context=True, aliases=["cc"])
	async def custom(self, ctx):
		if ctx.invoked_subcommand is None:
			return await self.bot.say('Missing Argument')

	@custom.command(pass_context=True)
	async def add(self, ctx, command, output, prefix_required = 0):
		print(prefix_required)

	@custom.command(pass_context=True)
	async def edit(self, ctx, *, command):
		pass

	@custom.command(pass_context=True)
	async def remove(self, ctx, *, command):
		pass

	@custom.command(pass_context=True)
	async def list(self, ctx, *, command):
		pass

def setup(Bot):
	Bot.add_cog(CustomCommands(Bot))