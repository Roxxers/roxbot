from discord.ext import commands
import load_config
from config.server_config import ServerConfig

def is_bot_owner():
	return commands.check(lambda ctx: ctx.message.author.id == load_config.owner)

def is_nfsw_enabled():
	return commands.check(lambda ctx: ServerConfig().load_config()[ctx.message.server.id]["nsfw"]["enabled"] == 1)

