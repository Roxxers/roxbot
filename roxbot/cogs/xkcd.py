import roxbot
from roxbot import guild_settings
from discord.ext import commands
from discord import Embed

async def lookup_num(num):
	return await roxbot.http.api_request("https://xkcd.com/{}/info.0.json".format(num))

async def lookup_latest():
	return await roxbot.http.api_request("https://xkcd.com/info.0.json")

async def lookup_title(title):
	return None # TODO

def comic_url(comic):
	return "https://xkcd.com/{}".format(comic["num"])

class Xkcd:
	def __init__(self, bot_client):
		self.bot = bot_client
		self.post_cache = {}
		for guild in self.bot.guilds:
			self.post_cache[guild.id] = [("", "")]

	@commands.command()
	@commands.has_permissions(add_reactions=True)
	@commands.bot_has_permissions(add_reactions=True)
	async def xkcd(self, ctx, arg):
		"""
		Grabs the image & metadata of the given xkcd comic
		Example:
		{command_prefix}xkcd 666
		{command_prefix}xkcd Silent Hammer
		"""

		# Check if passed a valid number
		if arg.isdigit():
			# If so, use that to look up
			comic = await lookup_num(int(arg))
		elif arg == "latest":
			# Get the latest comic
			comic = await lookup_latest()
		else:
			# Otherwise, assume it's meant to be a name & look up from that.
			comic = await lookup_title(arg)

		# If we couldn't find anything, return an error.
		if not comic:
			return await ctx.send("Error ;-; Couldn't find that comic.")
		else:
			# Otherwise, show the comic
			embed = Embed(title=comic["safe_title"], description="xkcd #{} by Randall Munroe".format(comic["num"]))
			embed.set_image(url=comic["img"])
			embed.set_footer(text=comic["alt"])
			embed.url = "http://xkcd.com/{}".format(comic["num"])
			output = await ctx.send(embed=embed)
			
			await roxbot.utils.delete_option(self.bot, ctx, output, self.bot.get_emoji(444410658101002261) or "❌")

def setup(bot_client):
	bot_client.add_cog(Xkcd(bot_client))
