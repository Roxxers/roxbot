import random
import requests

from html import unescape
from lxml import html
from bs4 import BeautifulSoup
from discord.ext.commands import bot

from Roxbot import checks
from Roxbot.logging import log
from Roxbot.settings import guild_settings

# Warning, this cog sucks so much but hopefully it works and doesn't break the bot too much.
# Just lazily edited old code and bodged it into this one.
# There is redundant code here that if removed would make it easier.

# Edit, cleaned up a lot more. But it still is a bit dodgy, when discord allows for the video object to be used in embeds, then we need to convert the cog to output embeds.


def _imgur_removed(url):
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	if "removed.png" in soup.img["src"]:
		return True
	else:
		return False


def imgur_get(url):
	if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv"):
		return url
	else:
		if _imgur_removed(url):
			return False
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		links = []
		for img in soup.find_all("img"):
			if "imgur" in img["src"]:
				if not img["src"] in links:
					links.append(img["src"])

		for video in soup.find_all("source"):
			if "imgur" in video["src"]:
				if not video["src"] in links:
					links.append(video["src"])
		if len(links) > 1:
			return url
		else:
			if "http" not in links[0]:
				links[0] = "https:" + links[0]
			return links[0]


def ero_get(url):
	if url.contains("eroshare"):
		url = "https://eroshae.com/" + url.split("/")[3]
	page = requests.get(url)
	tree = html.fromstring(page.content)
	links = tree.xpath('//source[@src]/@src')
	if links:
		return False
	links = tree.xpath('//*[@src]/@src')
	if len(links) > 2:
		return False
	for link in links:
		if "i." in link and "thumb" not in link:
			return "https:" + link


def subreddit_request(subreddit):
	options = [".json?count=1000", "/top/.json?sort=top&t=all&count=1000"]
	choice = random.choice(options)
	subreddit += choice
	r = requests.get("https://reddit.com/r/"+subreddit, headers={'User-agent': 'RoxBot Discord Bot'})
	try:
		reddit = r.json()["data"]
	except KeyError:
		return {}
	return reddit


def parse_url(url):
	if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv", "webm", "mp4", "webp"):
		return url
	if "imgur" in url:
		return imgur_get(url)
	elif "eroshare" in url or "eroshae" in url or "erome" in url:
		return ero_get(url)
	elif "gfycat" in url or "redd.it" in url or "i.reddituploads" in url or "media.tumblr" in url or "streamable" in url:
		return url
	else:
		return False

class Reddit():
	def __init__(self, bot_client):
		self.bot = bot_client

	@bot.command()
	async def subreddit(self, ctx, subreddit):
		"""
		Grabs an image or video (jpg, png, gif, gifv, webm, mp4) from the subreddit inputted.
		Example:
		{command_prefix}subreddit pics
		"""
		subreddit = subreddit.lower()
		links = subreddit_request(subreddit)
		title = ""

		if not links:
			return await ctx.send("Error ;-; That subreddit probably doesn't exist. Please check your spelling")
		else:
			if not links["after"]: # This is if we are given a search page that has links in it.
				return await ctx.send("Error ;-; That subreddit probably doesn't exist. Please check your spelling")

		url = ""
		for x in range(10):
			choice = random.choice(links["children"])
			if choice["data"]["over_18"] and not checks.nsfw_predicate(ctx):
				return await ctx.send("This server/channel doesn't have my NSFW stuff enabled. This extends to posting NFSW content from Reddit.")
			url = parse_url(choice["data"]["url"])
			if url:
				title = "**{}** \nby /u/{} from /r/{}\n".format(unescape(choice["data"]["title"]), unescape(choice["data"]["author"]), subreddit)
				break
		if not url:
			return await ctx.send("I couldn't find any images from that subreddit.")

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more.\n"
		else:
			text = ""

		if ctx.invoked_with == "subreddit":
			# Only log the command when it is this command being used. Not the inbuilt commands.
			logging = guild_settings.get(ctx.guild).logging
			log_channel = self.bot.get_channel(logging["channel"])
			await log(ctx.guild, log_channel, "subreddit", User=ctx.author, Subreddit=subreddit, Returned="<{}>".format(url), Channel=ctx.channel, Channel_Mention=ctx.channel.mention)

		return await ctx.send(title + text + url)

	@bot.command()
	async def aww(self, ctx):
		"""
		Gives you cute pics from reddit
		"""
		subreddit = "aww"
		return await ctx.invoke(self.subreddit, subreddit=subreddit)

	@bot.command()
	async def feedme(self, ctx):
		"""
		Feeds you with food porn. Uses multiple subreddits.
		Yes, I was very hungry when trying to find the subreddits for this command.
		Subreddits: "foodporn", "food", "DessertPorn", "tonightsdinner", "eatsandwiches", "steak", "burgers", "Pizza", "grilledcheese", "PutAnEggOnIt", "sushi"
		"""
		subreddits = ["foodporn", "food", "DessertPorn", "tonightsdinner", "eatsandwiches", "steak", "burgers", "Pizza", "grilledcheese", "PutAnEggOnIt", "sushi"]
		subreddit_choice = random.choice(subreddits)
		return await ctx.invoke(self.subreddit, subreddit=subreddit_choice)

	@bot.command()
	async def feedmevegan(self, ctx):
		"""
		Feeds you with vegan food porn. Uses multiple subreddits.
		Yes, I was very hungry when trying to find the subreddits for this command.
		Subreddits: "veganrecipes", "vegangifrecipes", "veganfoodporn"
		"""
		subreddits = ["veganrecipes", "vegangifrecipes", "VeganFoodPorn"]
		subreddit_choice = random.choice(subreddits)
		return await ctx.invoke(self.subreddit, subreddit=subreddit_choice)

	@bot.command(aliases=["gssp"])
	async def gss(self, ctx):
		"""
		Gives you the best trans memes ever
		"""
		subreddit = "gaysoundsshitposts"
		return await ctx.invoke(self.subreddit, subreddit=subreddit)


def setup(bot_client):
	bot_client.add_cog(Reddit(bot_client))
