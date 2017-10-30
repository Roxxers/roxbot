from discord.ext import commands
import load_config
#from config.server_config import ServerConfig

def is_bot_owner():
	return commands.check(lambda ctx: ctx.message.author.id == load_config.owner)
