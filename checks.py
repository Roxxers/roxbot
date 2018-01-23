from discord.ext import commands
import load_config
from config.server_config import ServerConfig
import discord

def is_bot_owner():
	return commands.check(lambda ctx: ctx.message.author.id == load_config.owner)

def is_owner_or_admin():
	def predicate(ctx):
		if ctx.message.author.id == load_config.owner:
			return True
		else:
			for role in ctx.message.author.roles:
				if role.id in ServerConfig().load_config()[ctx.message.server.id]["perm_roles"]["admin"]:
					return True
		return False
	return commands.check(predicate)

def is_nfsw_enabled():
	return commands.check(lambda ctx: ServerConfig().load_config()[ctx.message.server.id]["nsfw"]["enabled"] == 1)

def not_pm():
	return commands.check(lambda ctx: ctx.message.channel.type != discord.ChannelType.private)