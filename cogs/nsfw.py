import random
import checks
import requests
from discord.ext.commands import bot
from config.server_config import ServerConfig


class NFSW():
	def __init__(self, Bot):
		self.bot = Bot
		self.con = ServerConfig()
		self.servers = self.con.servers

	def is_nsfw_enabled(self, server_id):
		return self.servers[server_id]["nsfw"]["enabled"] == "1"

	def gelbooru_clone(self, base_url, tags):
		# Maybe a page randomiser
		limit = 100
		url = base_url + '/index.php?page=dapi&s=post&q=index&json=1&tags=' + tags + '&limit=' + str(limit)
		req = requests.get(url, headers={'User-agent': 'RoxBot Discord Bot'})
		#print(req.status_code)
		#print(req.content)
		#print(req.json)
		post = random.choice(req.json())
		return post

	@bot.command(pass_context=True)
	@checks.is_nfsw_enabled()
	async def e621(self, ctx, *, tags):
		"""
		Returns an image from e621.com and can use tags you provide.
		"""
		base_url = "https://e621.net/"
		limit = 150
		url = base_url + 'post/index.json?tags=' + tags + '&limit=' + str(limit)
		req = requests.get(url, headers = {'User-agent': 'RoxBot Discord Bot'})
		post = random.choice(req.json())
		return await self.bot.say(post["file_url"])

	@bot.command(pass_context=True)
	@checks.is_nfsw_enabled()
	async def rule34(self, ctx, *, tags):
		"""
		Returns an image from rule34.xxx and can use tags you provide.
		"""
		base_url = "https://rule34.xxx"
		post = self.gelbooru_clone(base_url, tags)
		url = "https://img.rule34.xxx/images/" + post["directory"] + "/" + post["image"]
		return await self.bot.say(url)

	@bot.command(pass_context=True)
	@checks.is_nfsw_enabled()
	async def gelbooru(self, ctx, *, tags):
		"""
		Returns an image from gelbooru.com and can use tags you provide.
		"""
		base_url = "https://gelbooru.com"
		post = self.gelbooru_clone(base_url, tags)
		url = "https://simg3.gelbooru.com/images/" + ''.join(post["directory"].split("\\")) + "/" + post["image"]
		return await self.bot.say(url)


def setup(Bot):
	Bot.add_cog(NFSW(Bot))