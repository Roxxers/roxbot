from discord.ext.commands import bot
from config.server_config import ServerConfig
from lxml import html
import os
import random
import requests
from bs4 import BeautifulSoup

# Warning, this cog sucks so much but hopefully it works and doesn't break the bot too much. Just lazily edited old code and bodged it into this one.
# There is redundant code here that if removed would make it easier. But it might be handy in the future and isn't that bad.


class RedditMedia:
	def get(self, url):
		return url


class Gfycat():
	def __init__(self):
		pass

	def url_get(self,url):
		urlsplit = url.split("/")
		urlsplit[2] = "giant." + urlsplit[2]
		urlsplit[-1] += ".gif"
		urlnew = "/".join(urlsplit)
		return urlnew

	def get(self,url):
		#url2 = self.url_get(url)
		url2 = url
		return url2


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
		#elif url.split(".")[-1] == "gifv":
		#	urlsplit = url.split(".")
		#	urlsplit[-1] = "gif"
		#	url = ".".join(urlsplit)
		#	return url"""
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
				print(links)
				if not "http" in links[0]:
					links[0] = "https:" + links[0]
				return links[0]


class Eroshare():
	def __init__(self):
		pass

	def album_create(self, name):
		self.album_create.hasbeencalled = True
		charlist = ("<", ">", '"', ":", "/", "|", "?", "*")
		# Can't use these in Windows Dir so next code used to remove chars from title
		for char in charlist:
			if char in name:
				name = name.replace(char, "")
		if name not in os.listdir("./"):
			os.mkdir("./" + name)
		os.chdir("./" + name)


	def get(self, url, name=None):
		if url.contains("eroshare"):
			url = "https://eroshae.com/" + url.split("/")[3]
		page = requests.get(url)
		tree = html.fromstring(page.content)
		links = tree.xpath('//source[@src]/@src')
		if links:
			return False
			#self.album_create(name)
			#for link in links:
			#	if "lowres" not in link:
			#		wget.download(link)
			#		print("Downloaded ", link)
		links = tree.xpath('//*[@src]/@src')
		if len(links) > 2: #and not self.album_create.hasbeencalled:
			return False
			#self.album_create(name)
		for link in links:
			if "i." in link and "thumb" not in link:
				return "https:" + link
				#if link.split("/")[-1] not in os.listdir("./"):
					#wget.download("https:" + link)
					#print("Downloaded ", link)
				#else:
				#	print("Already exists")
		#if album_create.hasbeencalled:
		#	os.chdir("../")
		#	album_create.hasbeencalled = False


class Tumblr():
	def get(self,url):
		return url


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
		url2 = ""
		if "imgur" in url:
			url2 = Imgur().get(url)
		elif "gfycat" in url:
			url2 = Gfycat().get(url)
		elif "eroshare" in url:
			url2 = Eroshare().get(url)
		elif "redd.it" in url or "i.reddituploads" in url:
			url2 = RedditMedia().get(url)
		elif "media.tumblr" in url:
			url2 = Tumblr().get(url)
		return url2


class Reddit():
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	@bot.command(pass_context=True)
	async def subreddit(self, ctx, subreddit):
		"""
		Grabs an image (png, gif, gifv, webm) from the subreddit inputted.
		Exmaple:
		{command_prefix}subreddit pics
		"""
		links = Scrapper().linkget(subreddit, True)
		title = ""
		if not links:
			return await self.bot.say("Error ;-; That subreddit probably doesn't exist. Please check your spelling")
		url = ""
		for x in range(10):
			choice = random.choice(links)
			title = "**{}** from /r/{}\n".format(choice["data"]["title"], subreddit)
			if choice["data"]["over_18"] and not self.servers[ctx.message.server.id]["nsfw"]["enabled"]:
				return await self.bot.say("This server doesn't have my NSFW stuff enabled. This extends to posting NFSW content from Reddit.")
			url = Scrapper().retriveurl(choice["data"]["url"])
			if url:
				break
		if not url:
			return await self.bot.say("I couldn't find any images from that subreddit.")

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more. "
		else:
			text = ""

		return await self.bot.say(title + text + url)


	@bot.command(pass_context=True)
	async def aww(self, ctx):
		"""
		Gives you cute pics from reddit
		"""
		subreddit = "aww"
		links = Scrapper().linkget(subreddit, True)
		if not links:
			return await self.bot.say("Error ;-; That subreddit probably doesn't exist. Please check your spelling")

		choice = random.choice(links)
		title = "**{}** from /r/{}\n".format(choice["data"]["title"], subreddit)
		if choice["data"]["over_18"] and not self.servers[ctx.message.server.id]["nsfw"]["enabled"]:
			return await self.bot.say(
				"This server doesn't have my NSFW stuff enabled. This extends to posting NFSW content from Reddit.")
		url = Scrapper().retriveurl(choice["data"]["url"])

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more. "
		else:
			text = ""
		return await self.bot.say(title + text + url)


	@bot.command(pass_context=True)
	async def feedme(self, ctx):
		"""
		Feeds you with food porn. Uses multiple subreddits
		Yes, I was very hungry when trying to find the subreddits for this command.
		"""
		subreddits = ["foodporn", "food", "DessertPorn", "tonightsdinner", "eatsandwiches", "steak", "burgers", "Pizza", "grilledcheese", "PutAnEggOnIt", "sushi"]
		subreddit = random.choice(subreddits)
		links = Scrapper().linkget(subreddit, True)
		if not links:
			return await self.bot.say("Error ;-; That subreddit probably doesn't exist. Please check your spelling")

		choice = random.choice(links)
		title = "**{}** from /r/{}\n".format(choice["data"]["title"], subreddit)
		if choice["data"]["over_18"] and not self.servers[ctx.message.server.id]["nsfw"]["enabled"]:
			return await self.bot.say(
				"This server doesn't have my NSFW stuff enabled. This extends to posting NFSW content from Reddit.")
		url = Scrapper().retriveurl(choice["data"]["url"])

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more. "
		else:
			text = ""
		return await self.bot.say(title + text + url)


	@bot.command(pass_context=True)
	async def traa(self, ctx):
		"""
		Gives you the best trans memes ever
		"""
		subreddit = "traaaaaaannnnnnnnnns"
		links = Scrapper().linkget(subreddit, True)
		if not links:
			return await self.bot.say("Error ;-; That subreddit probably doesn't exist. Please check your spelling")

		choice = random.choice(links)
		title = "**{}** from /r/{}\n".format(choice["data"]["title"], subreddit)
		if choice["data"]["over_18"] and not self.servers[ctx.message.server.id]["nsfw"]["enabled"]:
			return await self.bot.say(
				"This server doesn't have my NSFW stuff enabled. This extends to posting NFSW content from Reddit.")
		url = Scrapper().retriveurl(choice["data"]["url"])

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more. "
		else:
			text = ""
		return await self.bot.say(title + text + url)


def setup(Bot):
	Bot.add_cog(Reddit(Bot))