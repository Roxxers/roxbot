# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017-2018 Roxanne Gibson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import random
from html import unescape
from bs4 import BeautifulSoup

import discord
from discord.ext import commands

import roxbot
from roxbot import guild_settings


class Scrapper:
	# TODO: Reimplement eroshare, eroshae, and erome support. Also implement better api interaction with imgur now we require api key
	def __init__(self, cache_limit=10):
		self.post_cache = {}
		self.cache_limit = cache_limit

	@staticmethod
	async def _imgur_removed(url):
		page = await roxbot.http.get_page(url)
		soup = BeautifulSoup(page, 'html.parser')
		try:
			return bool("removed.png" in soup.img["src"])
		except TypeError:  # This should protect roxbot in case bs4 returns nothing.
			return False

	async def imgur_get(self, url):
		if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv"):
			return url
		else:
			if await self._imgur_removed(url):
				return False

			if not roxbot.imgur_token:
				return False

			base_endpoint = "https://api.imgur.com/3/"
			endpoint_album = base_endpoint + "album/{}/images.json".format(url.split("/")[-1])
			endpoint_image = base_endpoint + "image/{}.json".format(url.split("/")[-1])

			resp = await roxbot.http.api_request(endpoint_image,
												 headers={"Authorization": "Client-ID {}".format(roxbot.imgur_token)})
			if bool(resp["success"]) is True:
				return resp["data"]["link"]
			else:
				resp = await roxbot.http.api_request(endpoint_album,headers={"Authorization": "Client-ID {}".format(roxbot.imgur_token)})
				return resp["data"][0]["link"]

	async def parse_url(self, url):
		if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv", "webm", "mp4", "webp"):
			return url
		if "imgur" in url:
			return await self.imgur_get(url)
		elif "eroshare" in url or "eroshae" in url or "erome" in url:
			return None
		# return ero_get(url)
		elif "gfycat" in url or "redd.it" in url or "i.reddituploads" in url or "media.tumblr" in url or "streamable" in url:
			return url
		else:
			return None

	@staticmethod
	async def sub_request(subreddit):
		options = [".json?count=1000", "/top/.json?sort=top&t=all&count=1000"]
		choice = random.choice(options)
		subreddit += choice
		url = "https://reddit.com/r/" + subreddit
		r = await roxbot.http.api_request(url)
		try:
			posts = r["data"]
			# This part is to check for some common errors when doing a sub request
			# t3 is a post in a listing. We want to avoid not having this instead of a subreddit search, which would be t5.
			if not posts.get("after") or posts["children"][0]["kind"] != "t3":
				return {}
			return posts
		except (KeyError, TypeError):
			return {}

	def cache_refresh(self, cache_id):
		# IF ID is not in cache, create cache for ID
		if not self.post_cache.get(cache_id, False):
			self.post_cache[cache_id] = [("", "")]

	async def random(self, posts, subreddit, cache_id, nsfw_allowed, loop_amount=20):
		"""Function to pick a random post of a given list of reddit posts. Using the internal cache.
		Returns:
			None for failing to get a url that could be posted.
			A dict with the key success and the value False for failing the NSFW check
			or the post dict if getting the post is successful
		"""
		# This returns False if the subreddit is set the NSFW and the channel isn't.
		sub_search = await roxbot.http.api_request("https://reddit.com/subreddits/search.json?q={}".format(subreddit))
		for listing in sub_search["data"]["children"]:
			if listing["data"]["id"] == posts[0]["data"]["subreddit_id"].strip("t5_"):
				if listing["data"]["over18"] and not nsfw_allowed:
					return False

		# Loop to get the post randomly and make sure it hasn't been posted before
		url = None
		choice = None
		for x in range(loop_amount):
			choice = random.choice(posts)
			url = await self.parse_url(choice["data"]["url"])
			if url:
				# "over_18" is not a typo. For some fucking reason, reddit has "over_18" for posts, "over18" for subs.
				if not nsfw_allowed and choice["data"]["over_18"]:
					url = False  # Reject post and move to next loop
				else:
					# Check cache for post
					for cache in self.post_cache[cache_id]:
						if url in cache or choice["data"]["id"] in cache:
							continue
					break

		# This is for either a False (NSFW post not allowed) or a None for none.
		if url is None:
			return {}
		elif url is False:
			return {"success": False}
		# Cache post
		post = (choice["data"]["id"], url)
		self.post_cache[cache_id].append(post)
		# If too many posts in cache, remove oldest value.
		if len(self.post_cache[cache_id]) >= self.cache_limit:
			self.post_cache[cache_id].pop(0)
		return choice["data"]


class Reddit:
	def __init__(self, bot_client):
		self.bot = bot_client
		self.scrapper = Scrapper()

	@commands.command()
	@commands.has_permissions(add_reactions=True)
	@commands.bot_has_permissions(add_reactions=True)
	async def subreddit(self, ctx, subreddit):
		"""
		Grabs an image or video (jpg, png, gif, gifv, webm, mp4) from the subreddit inputted.
		Example:
		{command_prefix}subreddit pics
		"""
		subreddit = subreddit.lower()
		if isinstance(ctx.channel, discord.DMChannel):
			cache_id = ctx.author.id
		else:
			cache_id = ctx.guild.id

		self.scrapper.cache_refresh(cache_id)
		posts = await self.scrapper.sub_request(subreddit)
		if not posts:
			return await ctx.send("Error ;-; That subreddit probably doesn't exist. Please check your spelling")

		if isinstance(ctx.channel, discord.TextChannel):
			nsfw_allowed = ctx.channel.is_nsfw()
		else:
			nsfw_allowed = True

		choice = await self.scrapper.random(posts["children"], subreddit, cache_id, nsfw_allowed)

		if not choice:
			return await ctx.send("I couldn't find any images from that subreddit.")
		elif choice.get("success", True) is False:
			return await ctx.send("This channel isn't marked NSFW. The subreddit given or all posts found are NSFW.")

		title = "**{}** \nby /u/{} from /r/{}\n".format(unescape(choice["title"]), unescape(choice["author"]), subreddit)
		url = str(choice["url"])

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more.\n"
		else:
			text = ""

		if ctx.invoked_with == "subreddit" and isinstance(ctx.channel, discord.TextChannel):
			# Only log the command when it is this command being used. Not the inbuilt commands.
			logging = guild_settings.get(ctx.guild)["logging"]
			log_channel = ctx.guild.get_channel(logging["channel"])
			await roxbot.log(
				ctx.guild,
				log_channel,
				"subreddit",
				User=ctx.author,
				Subreddit=subreddit,
				Returned="<{}>".format(url),
				Channel=ctx.channel,
				Channel_Mention=ctx.channel.mention,
				Time=roxbot.datetime_formatting.format(ctx.message.created_at)
			)

		# Not using a embed here because we can't use video in rich embeds but they work in embeds now :/
		output = await ctx.send(title + text + url)
		await roxbot.utils.delete_option(self.bot, ctx, output, self.bot.get_emoji(444410658101002261) or "❌")

	@commands.command()
	async def aww(self, ctx):
		"""
		Gives you cute pics from reddit
		"""
		subreddit = "aww"
		return await ctx.invoke(self.subreddit, subreddit=subreddit)

	@commands.command()
	async def feedme(self, ctx):
		"""
		Feeds you with food porn. Uses multiple subreddits.
		Yes, I was very hungry when trying to find the subreddits for this command.
		Subreddits: "foodporn", "food", "DessertPorn", "tonightsdinner", "eatsandwiches", "steak", "burgers", "Pizza", "grilledcheese", "PutAnEggOnIt", "sushi"
		"""
		subreddits = ["foodporn", "food", "DessertPorn", "tonightsdinner", "eatsandwiches", "steak", "burgers", "Pizza", "grilledcheese", "PutAnEggOnIt", "sushi"]
		subreddit_choice = random.choice(subreddits)
		return await ctx.invoke(self.subreddit, subreddit=subreddit_choice)

	@commands.command()
	async def feedmevegan(self, ctx):
		"""
		Feeds you with vegan food porn. Uses multiple subreddits.
		Yes, I was very hungry when trying to find the subreddits for this command.
		Subreddits: "veganrecipes", "vegangifrecipes", "veganfoodporn"
		"""
		subreddits = ["veganrecipes", "vegangifrecipes", "VeganFoodPorn"]
		subreddit_choice = random.choice(subreddits)
		return await ctx.invoke(self.subreddit, subreddit=subreddit_choice)

	@commands.command(aliases=["gssp"])
	async def gss(self, ctx):
		"""
		Gives you the best trans memes ever
		"""
		subreddit = "gaysoundsshitposts"
		return await ctx.invoke(self.subreddit, subreddit=subreddit)


def setup(bot_client):
	bot_client.add_cog(Reddit(bot_client))
