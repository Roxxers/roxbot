import discord
import checks
from discord.ext.commands import group
from config.server_config import ServerConfig
import load_config

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
		elif len(msg.split(" ")) < 2:
			if msg.split(" ")[0] in self.servers[server]["custom_commands"]["0"]:
				return await self.bot.send_message(channel, self.servers[server]["custom_commands"]["0"][msg.split(" ")[0]])

	@group(pass_context=True, aliases=["cc"])
	@checks.is_owner_or_admin()
	async def custom(self, ctx):
		"A group of commands to manage custom commands for your server."
		if ctx.invoked_subcommand is None:
			return await self.bot.say('Missing Argument')

	@custom.command(pass_context=True)
	async def add(self, ctx, command, output, prefix_required = "0"):
		"Adds a custom command to the list of custom commands."
		self.servers = self.con.load_config()
		command = command.lower()
		output = output.lower()
		zero = self.servers[ctx.message.server.id]["custom_commands"]["0"]
		one = self.servers[ctx.message.server.id]["custom_commands"]["1"]

		if ctx.message.mentions:
			return await self.bot.say("Custom Commands cannot mention people.")
		elif len(output) > 1999: # This probably wont happen atm since the command itself would make the whole message over len 2000 which would be impossible to send. But this is here incase we need to adjust this number.
			return await self.bot.say("The output is too long")
		elif command in self.bot.commands and prefix_required == "1":
			return await self.bot.say("This is already the name of a built in command.")
		elif command in zero or command in one:
			return await self.bot.say("Custom Command already exists.")
		elif prefix_required != "1" and prefix_required != "0":
			return await self.bot.say("No prefix setting set.")

		self.servers[ctx.message.server.id]["custom_commands"][prefix_required][command] = output
		self.con.update_config(self.servers)
		return await self.bot.say("{} has been added with the output: '{}'".format(command, output))

	@custom.command(pass_context=True)
	async def edit(self, ctx, command, edit):
		"Edits an existing custom command."
		self.servers = self.con.load_config()
		zero = self.servers[ctx.message.server.id]["custom_commands"]["0"]
		one = self.servers[ctx.message.server.id]["custom_commands"]["1"]

		if ctx.message.mentions:
			return await self.bot.say("Custom Commands cannot mention people.")

		if command in zero:
			self.servers[ctx.message.server.id]["custom_commands"]["0"][command] = edit
			self.con.update_config(self.servers)
			return await self.bot.say("Edit made. {} now outputs {}".format(command, edit))
		elif command in one:
			self.servers[ctx.message.server.id]["custom_commands"]["1"][command] = edit
			self.con.update_config(self.servers)
			return await self.bot.say("Edit made. {} now outputs {}".format(command, edit))
		else:
			return await self.bot.say("That Custom Command doesn't exist.")

	@custom.command(pass_context=True)
	async def remove(self, ctx, command):
		"Removes a custom command."
		self.servers = self.con.load_config()
		command = command.lower()
		if command in self.servers[ctx.message.server.id]["custom_commands"]["1"]:
			self.servers[ctx.message.server.id]["custom_commands"]["1"].pop(command)
			self.con.update_config(self.servers)
			return await self.bot.say("Removed {} custom command".format(command))
		elif command in self.servers[ctx.message.server.id]["custom_commands"]["0"]:
			self.servers[ctx.message.server.id]["custom_commands"]["0"].pop(command)
			self.con.update_config(self.servers)
			return await self.bot.say("Removed {} custom command".format(command))
		else:
			return await self.bot.say("Custom Command doesn't exist.")


	@custom.command(pass_context=True)
	async def list(self, ctx, debug="0"):
		"Lists all custom commands for this server."
		if debug != "0" and debug != "1":
			debug = "0"
		self.servers = self.con.load_config()
		l = self.servers[ctx.message.server.id]["custom_commands"]
		listzero = ""
		listone = ""

		for command in l["0"]:
			if debug == "1":
				command += command + " - {}".format(l["0"][command])
			listzero = listzero + "- " + command + "\n"
		for command in l["1"]:
			if debug == "1":
				command += command + " - {}".format(l["1"][command])
			listone = listone + "- " + command + "\n"
		if not listone:
			listone = "There are no commands setup.\n"
		if not listzero:
			listzero = "There are no commands setup.\n"
		em = discord.Embed(title="Here is the list of Custom Commands", color=load_config.embedcolour)
		em.add_field(name="Commands that require Prefix:", value=listone, inline=False)
		em.add_field(name="Commands that don't:", value=listzero, inline=False)
		return await self.bot.say(embed=em)

def setup(Bot):
	Bot.add_cog(CustomCommands(Bot))