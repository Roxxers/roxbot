import discord
import random


class Reddit():
	def __init__(self, Bot):
		self.bot = Bot

	@bot.command(pass_context=True)
	async def reddit(self, ctx, subreddit):
		links = scrapper().linkget(subreddit, True)
		if not links:
			return await self.bot.say("Error ;-; That subreddit probably doesn't exist. Please check your spelling")
		url = ""
		while not url:
			choice = random.choice(links)
			url = scrapper().retriveurl(choice["data"]["url"])

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more. "
		else:
			text = ""
		return await self.bot.say(text + url)


	@bot.command()
	async def aww(self):
		links = scrapper().linkget("aww", True)
		if not links:
			return await self.bot.say("Error ;-; That subreddit probably doesn't exist. Please check your spelling")
		url = ""
		while not url:
			choice = random.choice(links)
			url = scrapper().retriveurl(choice["data"]["url"])

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more. "
		else:
			text = ""
		return await self.bot.say(text + url)

def setup(Bot):
	Bot.add_cog(Reddit(Bot))