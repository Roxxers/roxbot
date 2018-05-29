import roxbot
from roxbot import guild_settings
from discord.ext import commands
from discord import Embed

TITLE_QUERY_URL="http://www.explainxkcd.com/wiki/api.php?format=json&action=query&redirects&titles={}"
XKCD_SITE="https://xkcd.com{}"

async def lookup_num(num):
	return await roxbot.http.api_request(XKCD_SITE.format(num + "/info.0.json"))

async def lookup_latest():
	return await roxbot.http.api_request(XKCD_SITE.format("/info.0.json"))

async def lookup_title(title):
	api = await roxbot.http.api_request(TITLE_QUERY_URL.format(title.replace(" ", "_")))
	# if valid, query.redirects.to is the full & proper page title, including the actual number.
	try:
		full_page_title = api["query"]["redirects"][0]["to"]
		num = full_page_title.split(":")[0]
		return await lookup_num(num)
	except KeyError: # this means query,redirects... didn't exist, done like this to save a massive if statement.
		return None

class Xkcd:
	"""
	Cog for looking up and linking xkcd comics.
	"""
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
		{command_prefix}xkcd latest
		"""
		async with ctx.typing():
			# Check if passed a valid number
			if arg.isdigit():
				# If so, use that to look up
				comic = await lookup_num(int(arg))
			elif arg == "latest":
				# Get the latest comic
				comic = await lookup_latest()
			else:
				# Otherwise, assume it's meant to be a name & look up from that.
				# Get the full input; not just the first word and also fix the caps.
				arg = " ".join(ctx.message.content.split(" ")[1:]).title()
				
				comic = await lookup_title(arg)

		# If we couldn't find anything, return an error.
		if not comic:
			return await ctx.send("{} - Couldn't find that comic.".format(ctx.message.author.mention))
		else:
			# Otherwise, show the comic
			embed = Embed(title=comic["safe_title"], description="xkcd #{} by Randall Munroe".format(comic["num"]))
			embed.set_image(url=comic["img"])
			embed.set_footer(text=comic["alt"])
			embed.url = XKCD_SITE.format(comic["num"])
			output = await ctx.send(embed=embed)
			
			await roxbot.utils.delete_option(self.bot, ctx, output, self.bot.get_emoji(444410658101002261) or "❌")

def setup(bot_client):
	bot_client.add_cog(Xkcd(bot_client))
