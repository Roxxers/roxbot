import random
from html import unescape
from bs4 import BeautifulSoup
from discord.ext.commands import bot

import roxbot
from roxbot import guild_settings


async def _imgur_removed(url):
	page = await roxbot.http.get_page(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	if "removed.png" in soup.img["src"]:
		return True
	else:
		return False


async def imgur_get(url):
	if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv"):
		return url
	else:
		if await _imgur_removed(url):
			return False
		page = await roxbot.http.get_page(url)
		soup = BeautifulSoup(page, 'html.parser')
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

# TODO: Reimplement eroshare, eroshae, and erome support.

async def subreddit_request(subreddit):
	options = [".json?count=1000", "/top/.json?sort=top&t=all&count=1000"]
	choice = random.choice(options)
	subreddit += choice
	url = "https://reddit.com/r/"+subreddit
	r = await roxbot.http.api_request(url)
	try:
		posts = r["data"]
		return posts
	except KeyError or TypeError:
		return {}


async def parse_url(url):
	if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv", "webm", "mp4", "webp"):
		return url
	if "imgur" in url:
		return await imgur_get(url)
	elif "eroshare" in url or "eroshae" in url or "erome" in url:
		return False
		#return ero_get(url)
	elif "gfycat" in url or "redd.it" in url or "i.reddituploads" in url or "media.tumblr" in url or "streamable" in url:
		return url
	else:
		return False


class Reddit():
	def __init__(self, bot_client):
		self.bot = bot_client
		self.post_cache = {}
		for guild in self.bot.guilds:
			self.post_cache[guild.id] = [("", "")]

	@bot.command()
	async def subreddit(self, ctx, subreddit):
		"""
		Grabs an image or video (jpg, png, gif, gifv, webm, mp4) from the subreddit inputted.
		Example:
		{command_prefix}subreddit pics
		"""
		subreddit = subreddit.lower()
		links = await subreddit_request(subreddit)
		title = ""
		choice = {}

		if not links or not links.get("after") or links["children"][0]["kind"] == "t5":  # The second part is if we are given a search page that has links in it.
			return await ctx.send("Error ;-; That subreddit probably doesn't exist. Please check your spelling")

		url = ""
		x = 0
		# While loop here to make sure that we check if there is any image posts in the links we have. If so, just take the first one.
		# Choosing a while loop here because, for some reason, the for loop would never exit till the end. Leading to slow times.
		while not url or not x > 20:
			choice = random.choice(links["children"])["data"]
			url = await parse_url(choice["url"])
			if url:
				x_old = int(x)
				# If the url or id are in the cache,  continue the loop. If not, proceed with the post.
				for cache in self.post_cache[ctx.guild.id]:
					if url in cache or choice["id"] in cache:
						x += 1
						break
				if x_old != x:  # Has x been incremented
					url = ""  # Restart search for new post
					continue

				title = "**{}** \nby /u/{} from /r/{}\n".format(unescape(choice["title"]), unescape(choice["author"]),subreddit)
				break

		# Check if post is NSFW, and if it is and this channel doesn't past the NSFW check, then return with the error message.
		if choice["over_18"] and not roxbot.checks.nsfw_predicate(ctx):
			return await ctx.send("This server/channel doesn't have my NSFW stuff enabled. This extends to posting NFSW content from Reddit.")
		if not url:  # If no image posts could be found with the for loop.
			return await ctx.send("I couldn't find any images from that subreddit.")

		# Put the post ID and url in the cache. The url is used in case of two posts having the same link. Handy to avoid crossposts getting through the cache.
		cache_amount = 10
		post = (choice["id"], url)
		self.post_cache[ctx.guild.id].append(post)
		if len(self.post_cache[ctx.guild.id]) >= cache_amount:
			self.post_cache[ctx.guild.id].pop(0)

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more.\n"
		else:
			text = ""

		if ctx.invoked_with == "subreddit":
			# Only log the command when it is this command being used. Not the inbuilt commands.
			logging = guild_settings.get(ctx.guild).logging
			log_channel = self.bot.get_channel(logging["channel"])
			await roxbot.log(ctx.guild, log_channel, "subreddit", User=ctx.author, Subreddit=subreddit, Returned="<{}>".format(url), Channel=ctx.channel, Channel_Mention=ctx.channel.mention)

		# Not using a embed here because we can't use video in rich embeds but they work in embeds now :/
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

	@bot.command(hidden=True, name="subreddit_dryrun")
	async def _subreddit_test(self, ctx, url):
		return await ctx.send(await parse_url(url))


def setup(bot_client):
	bot_client.add_cog(Reddit(bot_client))
