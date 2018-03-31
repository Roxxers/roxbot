from discord.ext.commands import bot
from lxml import html
import random
import requests
from bs4 import BeautifulSoup
from Roxbot import checks


# Warning, this cog sucks so much but hopefully it works and doesn't break the bot too much. Just lazily edited old code and bodged it into this one.
# There is redundant code here that if removed would make it easier. But it might be handy in the future and isn't that bad.

class Imgur():
	"""Class for all interactions with Imgur"""
	def __init__(self):
		pass

	def removed(self,url):
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		if "removed.png" in soup.img["src"]:
			return True
		else:
			return False

	def get(self, url):
		if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv"):
			return url
		else:
			if self.removed(url):
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
				if not "http" in links[0]:
					links[0] = "https:" + links[0]
				return links[0]

class Eroshare():
	def __init__(self):
		pass

	def get(self, url, name=None):
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

class Scrapper():
	def __init__(self):
		pass

	def linkget(self, subreddit, israndom):
		if israndom:
			options = [".json?count=1000", "/top/.json?sort=top&t=all&count=1000"]
			choice = random.choice(options)
			subreddit += choice
		html = requests.get("https://reddit.com/r/"+subreddit, headers = {'User-agent': 'RoxBot Discord Bot'})
		try:
			reddit = html.json()["data"]["children"]
		except KeyError:
			return False
		return reddit

	def retriveurl(self, url):
		if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv", "webm", "mp4", "webp"):
			return url
		if "imgur" in url:
			return Imgur().get(url)
		elif "eroshare" in url:
			return Eroshare().get(url)
		elif "gfycat" in url or "redd.it" in url or "i.reddituploads" in url or "media.tumblr" in url or "streamable" in url:
			return url

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
		links = Scrapper().linkget(subreddit, True)
		title = ""
		if not links:
			return await ctx.send("Error ;-; That subreddit probably doesn't exist. Please check your spelling")
		url = ""
		for x in range(10):
			choice = random.choice(links)
			title = "**{}** from /r/{}\n".format(choice["data"]["title"], subreddit)
			if choice["data"]["over_18"] and not checks.nsfw_predicate(ctx):
				return await ctx.send("This server/channel doesn't have my NSFW stuff enabled. This extends to posting NFSW content from Reddit.")
			url = Scrapper().retriveurl(choice["data"]["url"])
			if url:
				break
		if not url:
			return await ctx.send("I couldn't find any images from that subreddit.")

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more. "
		else:
			text = ""

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