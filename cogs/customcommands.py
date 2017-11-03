from discord.ext.commands import bot
from discord.ext.commands import group
from config.server_config import ServerConfig

# TODO: Sort out admin commands, mod commands, the settings before ever pushing this to general use. It needs to be a mod only thing.

class CustomCommands():
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	async def on_message(self, message):
		msg = message.content.lower()
		channel = message.channel
		server = message.server.id
		if message.author == self.bot.user:
			return
		if msg.startswith(self.bot.command_prefix):
			if msg.split(self.bot.command_prefix)[1] in self.servers[server]["custom_commands"]["1"]:
				return await self.bot.send_message(channel, self.servers[server]["custom_commands"]["1"][msg.split(self.bot.command_prefix)[1]])
		elif len(msg.split(" ")) < 3:
			if msg.split(" ")[0] in self.servers[server]["custom_commands"]["0"]:
				return await self.bot.send_message(channel, self.servers[server]["custom_commands"]["0"][msg.split(" ")[0]])


	@group(pass_context=True, aliases=["cc"])
	async def custom(self, ctx):
		if ctx.invoked_subcommand is None:
			return await self.bot.say('Missing Argument')

	@custom.command(pass_context=True)
	async def add(self, ctx, command, output, prefix_required = "0"):
		command = command.lower()
		output = output.lower()
		if prefix_required != "1" and prefix_required != "0":
			return await self.bot.say("No prefix setting set.")
		self.servers[ctx.message.server.id]["custom_commands"][prefix_required][command] = output
		self.con.update_config(self.servers)
		return await self.bot.say("{} has been added with the output: '{}'".format(command, output))

	@custom.command(pass_context=True)
	async def edit(self, ctx, *, command):
		try:
			self.servers[ctx.message.server.id]["custom_commands"]["1"]["command"].popout()
		except KeyError:
			print("It worked")

	@custom.command(pass_context=True)
	async def remove(self, ctx, command):
		command = command.lower()
		try:
			if command in self.servers[ctx.message.server.id]["custom_commands"]["1"]:
				self.servers[ctx.message.server.id]["custom_commands"]["1"][command].popout()
		except:
			print("It worked")


	@custom.command(pass_context=True)
	async def list(self, ctx, *, command):
		command = command.lower()

def setup(Bot):
	Bot.add_cog(CustomCommands(Bot))