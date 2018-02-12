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

def is_admin_or_mod():
	def predicate(ctx):
		if ctx.message.author.id == load_config.owner:
			return True
		else:
			admin_roles =  ServerConfig().load_config()[ctx.message.server.id]["perm_roles"]["admin"]
			mod_roles = ServerConfig().load_config()[ctx.message.server.id]["perm_roles"]["mod"]
			for role in ctx.message.author.roles:
				if role.id in mod_roles or role.id in admin_roles:
					return True
		return False
	return commands.check(predicate)

def nsfw_predicate(ctx):
	nsfw = ServerConfig().load_config()[ctx.message.server.id]["nsfw"]
	if not nsfw["channels"] and nsfw["enabled"]:
		return nsfw["enabled"] == 1
	elif nsfw["enabled"] and nsfw["channels"]:
		return ctx.message.channel.id in nsfw["channels"]
	else:
		print("yo")
		return False

def is_nfsw_enabled():
	return commands.check(lambda ctx: nsfw_predicate(ctx))



def not_pm():
	return commands.check(lambda ctx: ctx.message.channel.type != discord.ChannelType.private)