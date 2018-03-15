from discord.ext import commands
import load_config
from config.server_config import ServerConfig

def is_owner_or_admin():
	def predicate(ctx):
		if ctx.author.id == load_config.owner:
			return True
		else:
			for role in ctx.author.roles:
				if role.id in ServerConfig().load_config()[str(ctx.guild.id)]["perm_roles"]["admin"]:
					return True
		return False
	return commands.check(predicate)

def is_admin_or_mod():
	def predicate(ctx):
		if ctx.message.author.id == load_config.owner:
			return True
		else:
			admin_roles =  ServerConfig().load_config()[str(ctx.guild.id)]["perm_roles"]["admin"]
			mod_roles = ServerConfig().load_config()[str(ctx.guild.id)]["perm_roles"]["mod"]
			for role in ctx.author.roles:
				if role.id in mod_roles or role.id in admin_roles:
					return True
		return False
	return commands.check(predicate)

def nsfw_predicate(ctx):
	nsfw = ServerConfig().load_config()[str(ctx.guild.id)]["nsfw"]
	if not nsfw["channels"] and nsfw["enabled"]:
		return nsfw["enabled"] == 1
	elif nsfw["enabled"] and nsfw["channels"]:
		return ctx.channel.id in nsfw["channels"]
	else:
		return False

def is_nfsw_enabled():
	return commands.check(lambda ctx: nsfw_predicate(ctx))

def isnt_anal():
	return commands.check(lambda ctx: ServerConfig().load_config()[str(ctx.guild.id)]["is_anal"]["y/n"] and nsfw_predicate(ctx) or not ServerConfig().load_config()[str(ctx.guild.id)]["is_anal"]["y/n"])
