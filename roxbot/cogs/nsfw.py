import random
from discord.ext.commands import bot

import roxbot
from roxbot import guild_settings as gs


def tag_blacklist(guild):
	blacklist = ""
	for tag in gs.get(guild).nsfw["blacklist"]:
		blacklist += "-{} ".format(tag)
	return blacklist


class NFSW():
	def __init__(self, bot_client):
		self.bot = bot_client
		self.cache = {}
		for guild in self.bot.guilds:
			self.cache[guild.id] = []

	@roxbot.checks.is_nfsw_enabled()
	@bot.command(hidden=True)
	async def gelbooru_clone(self, ctx, base_url, post_url, tags):
		limit = 150
		tags = tags + tag_blacklist(ctx.guild)
		url = base_url + tags + '&limit=' + str(limit)

		posts = await roxbot.http.api_request(url)

		if posts is None:
			return await ctx.send("Nothing was found. *psst, check the tags you gave me.*")

		post = None
		counter = 0
		while counter < 20:
			post = random.choice(posts)
			md5 = post.get("md5") or post.get("hash")
			if md5 not in self.cache[ctx.guild.id]:
				self.cache[ctx.guild.id].append(md5)
				if len(self.cache[ctx.guild.id]) > 10:
					self.cache[ctx.guild.id].pop(0)
				break
			counter += 1

		url = post.get("file_url")
		if not url:
			url = post_url + "{0[directory]}/{0[image]}".format(post)
		output = await ctx.send(url)
		await roxbot.utils.delete_option(self.bot, ctx, output, self.bot.get_emoji(444410658101002261) or "❌")

	@roxbot.checks.is_nfsw_enabled()
	@bot.command()
	async def e621(self, ctx, *, tags=""):
		"""
		Returns an image from e621.com and can use tags you provide.
		"""
		base_url = "https://e621.net/post/index.json?tags="
		return await ctx.invoke(self.gelbooru_clone, base_url=base_url, post_url="", tags=tags)

	@roxbot.checks.is_nfsw_enabled()
	@bot.command()
	async def rule34(self, ctx, *, tags=""):
		"""
		Returns an image from rule34.xxx and can use tags you provide.
		"""
		base_url = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags="
		post_url = "https://img.rule34.xxx/images/"
		return await ctx.invoke(self.gelbooru_clone, base_url=base_url, post_url=post_url, tags=tags)

	@roxbot.checks.is_nfsw_enabled()
	@bot.command()
	async def gelbooru(self, ctx, *, tags=""):
		"""
		Returns an image from gelbooru.com and can use tags you provide.
		"""
		base_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="
		post_url = "https://simg3.gelbooru.com/images/"
		return await ctx.invoke(self.gelbooru_clone, base_url=base_url, post_url=post_url, tags=tags)


def setup(bot_client):
	bot_client.add_cog(NFSW(bot_client))
