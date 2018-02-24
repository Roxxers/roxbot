import requests
from html import unescape
import load_config
import asyncio
from discord.ext.commands import group


class Trivia:
	"""
	Trivia is based off the lovely https://opentdb.com made by PixelTail Games.
	"""
	def __init__(self, bot_client):
		self.bot = bot_client
		self.games = {}

	def get_questions(self, amount=10):
		r = requests.get("https://opentdb.com/api.php?amount={}".format(amount))
		return r.json()

	async def game(self, ctx, channel, questions):
		# make sure to check that there is still players playing after a question
		for question in questions:
			"""Category: {}
			Difficulty: {}
			Question: {}
			
			""".format(question["category"], question["difficulty"], unescape(question[question]))
			if question["type"] == "boolean":
				"t"
			await ctx.send(question)


	@group()
	async def trivia(self, ctx):
		pass

	@trivia.command()
	async def start(self, ctx, amount = "medium"):
		channel = ctx.channel
		player = ctx.author
		# Check if a game is already running and if so exit.
		if channel.id in self.games:
			# Game active in this channel already
			await ctx.send("A game is already being run in this channel.", delete_after=2)
			await asyncio.sleep(2)
			return await ctx.message.delete()

		# Setup variables and wait for all players to join.
		length = {"short": 5, "medium": 10, "long": 15}
		if amount not in length:
			amount = "medium"
		game = {"players":  {player.id: 0}, "active": 0, "length": length[amount]}
		self.games[channel.id] = game
		await ctx.send("Game Successfully created. Starting in 20 seconds...")
		await asyncio.sleep(20)
		questions = self.get_questions(length[amount])
		# Ehecks if there is any players to play the game still
		if not self.games[channel.id]["players"]:
			self.games.pop(channel.id)
			return await ctx.send("Abandoning game due to lack of players.")

		# Starts game
		self.games[channel.id]["active"] = 1
		await ctx.send("GAME START")
		await self.game(ctx, channel, questions["results"])
		# FOR LOOP FOR THE GAME CAUSE THAT WILL WORK

	@trivia.command()
	async def join(self, ctx):
		channel = ctx.channel
		# Checks if game is in this channel. Then if one isn't active, then if the player has already joined.
		if channel.id in self.games:
			if not self.games[channel.id]["active"]:
				player = ctx.author
				if player.id not in self.games[channel.id]["players"]:
					self.games[channel.id]["players"][player.id] = 0
					return await ctx.send("Player {} joined the game".format(player.mention))
				# Failures
				else:
					await ctx.send("You have already joined the game. If you want to leave, do `{}trivia leave`".format(load_config.command_prefix), delete_after=2)
					await asyncio.sleep(2)
					return await ctx.message.delete()
			else:
				await ctx.send("Game is already in progress.", delete_after=2)
				await asyncio.sleep(2)
				return await ctx.message.delete()
		else:
			await ctx.send("Game isn't being played here.", delete_after=2)
			await asyncio.sleep(2)
			return await ctx.message.delete()

	@trivia.command()
	async def leave(self, ctx):
		channel = ctx.channel
		player = ctx.author
		# CAN LEAVE:  Game is started or has been activated
		# CANT LEAVE: Game is not active or not in the game
		if channel.id in self.games:
			if player.id in self.games[channel.id]["players"]:
				self.games[channel.id]["players"].pop(player.id)
				await ctx.send("{} has left the game.".format(player.mention))
				return await ctx.message.delete()
			else:
				await ctx.send("You are not in this game", delete_after=2)
				await asyncio.sleep(2)
				return await ctx.message.delete()
		else:
			await ctx.send("Game isn't being played here.", delete_after=2)
			await asyncio.sleep(2)
			return await ctx.message.delete()

def setup(Bot):
	Bot.add_cog(Trivia(Bot))