import discord
import checks
from discord.ext.commands import group
from config.server_config import ServerConfig
import load_config

def blacklisted(user):
	with open("config/blacklist.txt", "r") as fp:
		for line in fp.readlines():
			if user.id+"\n" == line:
				return True
	return False


class CustomCommands():
	def __init__(self, bot_client):
		self.bot = bot_client
		self.con = ServerConfig()
		self.servers = self.con.servers

	async def on_message(self, message):
		if blacklisted(message.author) or type(message.channel) != discord.TextChannel:
			return
		msg = message.content.lower()
		channel = message.channel
		server = str(message.guild.id)
		if message.author == self.bot.user:
			return
		if msg.startswith(self.bot.command_prefix):
			if msg.split(self.bot.command_prefix)[1] in self.servers[server]["custom_commands"]["1"]:
				return await channel.send(self.servers[server]["custom_commands"]["1"][msg.split(self.bot.command_prefix)[1]])
		elif len(msg.split(" ")) < 2:
			if msg.split(" ")[0] in self.servers[server]["custom_commands"]["0"]:
				return await channel.send(self.servers[server]["custom_commands"]["0"][msg.split(" ")[0]])

	@group(pass_context=True, aliases=["cc"])
	@checks.is_owner_or_admin()
	async def custom(self, ctx):
		"A group of commands to manage custom commands for your server."
		if ctx.invoked_subcommand is None:
			return await ctx.send('Missing Argument')

	@custom.command(pass_context=True)
	async def add(self, ctx, command, output, prefix_required = "0"):
		"Adds a custom command to the list of custom commands."
		self.servers = self.con.load_config()
		command = command.lower()
		output = output
		zero = self.servers[str(ctx.guild.id)]["custom_commands"]["0"]
		one = self.servers[str(ctx.guild.id)]["custom_commands"]["1"]

		if ctx.message.mentions or ctx.message.mention_everyone or ctx.message.role_mentions:
			return await ctx.send("Custom Commands cannot mention people/roles/everyone.")
		elif len(output) > 1800:
			return await ctx.send("The output is too long")
		elif command in self.bot.commands and prefix_required == "1":
			return await ctx.send("This is already the name of a built in command.")
		elif command in zero or command in one:
			return await ctx.send("Custom Command already exists.")
		elif prefix_required != "1" and prefix_required != "0":
			return await ctx.send("No prefix setting set.")
		elif len(command.split(" ")) > 1 and prefix_required == "1":
			return await ctx.send("Custom commands with a prefix can only be one word with no spaces.")

		self.servers[str(ctx.guild.id)]["custom_commands"][prefix_required][command] = output
		self.con.update_config(self.servers)
		return await ctx.send("{} has been added with the output: '{}'".format(command, output))

	@custom.command(pass_context=True)
	async def edit(self, ctx, command, edit):
		"Edits an existing custom command."
		self.servers = self.con.load_config()
		zero = self.servers[str(ctx.guild.id)]["custom_commands"]["0"]
		one = self.servers[str(ctx.guild.id)]["custom_commands"]["1"]

		if ctx.message.mentions or ctx.message.mention_everyone or ctx.message.role_mentions:
			return await ctx.send("Custom Commands cannot mention people/roles/everyone.")

		if command in zero:
			self.servers[str(ctx.guild.id)]["custom_commands"]["0"][command] = edit
			self.con.update_config(self.servers)
			return await ctx.send("Edit made. {} now outputs {}".format(command, edit))
		elif command in one:
			self.servers[str(ctx.guild.id)]["custom_commands"]["1"][command] = edit
			self.con.update_config(self.servers)
			return await ctx.send("Edit made. {} now outputs {}".format(command, edit))
		else:
			return await ctx.send("That Custom Command doesn't exist.")

	@custom.command(pass_context=True)
	async def remove(self, ctx, command):
		"Removes a custom command."
		self.servers = self.con.load_config()
		command = command.lower()
		if command in self.servers[str(ctx.guild.id)]["custom_commands"]["1"]:
			self.servers[str(ctx.guild.id)]["custom_commands"]["1"].pop(command)
			self.con.update_config(self.servers)
			return await ctx.send("Removed {} custom command".format(command))
		elif command in self.servers[str(ctx.guild.id)]["custom_commands"]["0"]:
			self.servers[str(ctx.guild.id)]["custom_commands"]["0"].pop(command)
			self.con.update_config(self.servers)
			return await ctx.send("Removed {} custom command".format(command))
		else:
			return await ctx.send("Custom Command doesn't exist.")


	@custom.command(pass_context=True)
	async def list(self, ctx, debug="0"):
		"Lists all custom commands for this server."
		if debug != "0" and debug != "1":
			debug = "0"
		self.servers = self.con.load_config()
		l = self.servers[str(ctx.guild.id)]["custom_commands"]
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

		# TODO: Sort out a way to shorten this if it goes over 2000 characters.
		
		em = discord.Embed(title="Here is the list of Custom Commands", color=load_config.embedcolour)
		em.add_field(name="Commands that require Prefix:", value=listone, inline=False)
		em.add_field(name="Commands that don't:", value=listzero, inline=False)
		return await ctx.send(embed=em)

def setup(bot_client):
	bot_client.add_cog(CustomCommands(bot_client))