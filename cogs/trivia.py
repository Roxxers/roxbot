# -*- coding: utf-8 -*-

import discord
import asyncio
import requests
import datetime
from html import unescape
from random import shuffle
from discord.ext.commands import group, bot


"""
Notes for myself.
Game logic

START
WAIT FOR USERS WITH JOIN AND LEAVE
START GAME FUNCTION

LOOP:
PARSE QUESTIONS
ADD REACTION
CORRECT ANSWER SCREEN
ADD SCORES
END

END SCORES AND WINNER SCREEN"""


class Trivia:
	"""
	Trivia is based off the lovely https://opentdb.com made by PixelTail Games.

	This cog requires the bot account to be in the Roxbot Emoji Server to work.
	"""
	def __init__(self, bot_client):
		# Get emoji objects here for the reactions. Basically to speedup the reactions for the game.
		# For some reason this is quicker than bot.get_emojis
		a_emoji = discord.utils.get(self.bot.emojis, id=419572828854026252)
		b_emoji = discord.utils.get(self.bot.emojis, id=419572828925329429)
		c_emoji = discord.utils.get(self.bot.emojis, id=419572829231775755)
		d_emoji = discord.utils.get(self.bot.emojis, id=419572828954820620)
		self.emojis = [a_emoji, b_emoji, c_emoji, d_emoji]
		self.bot = bot_client
		self.games = {}

	def get_questions(self, amount=10):
		r = requests.get("https://opentdb.com/api.php?amount={}&type=boolean".format(amount))
		return r.json()

	def parse_question(self, question):
		output = "Category: {}\nDifficulty: {}\nQuestion: {}\n".format(question["category"], question["difficulty"],
																	   unescape(question["question"]))
		if question["type"] == "boolean":
			choices = ["True", "False"]
			answers = "{} {}\n{} {}".format(str(self.emojis[0]), choices[0], str(self.emojis[1]), choices[1])
			output += answers
		elif question["type"] == "multiple":
			pass
		return output

	async def add_question_reactions(self, message, question):
		if question["type"] == "boolean":
			amount = 2
		else:
			amount = 4
		for x in range(amount):
			await message.add_reaction(self.emojis[x])

	async def on_reaction_add(self, reaction, user):
		"""Logic for answering a question"""
		if reaction.me or user.id in self.games[reaction.message.channel.id]["answered"]:
			return
		elif reaction.emoji in self.emojis and reaction.message == self.games[reaction.message.channel.id]["current_question"]:
			pass

	async def game(self, ctx, channel, questions):
		for question in questions:
			output = self.parse_question(question)
			message  = await ctx.send("Waiting for reacts")
			await self.add_question_reactions(message, question)
			await message.edit(content=output)
			self.games[ctx.channel.id]["current_question"] = message
			await asyncio.sleep(10)
			await message.clear_reactions()
			# Correct answer
			# Scores
			# Display that
			# make sure to check that there is still players playing after a question


		# Game Naturally Ends
		# Some stuff here displaying score

		self.games.pop(channel.id)
		await ctx.send("GAME END")


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
		# Length of game
		length = {"short": 5, "medium": 10, "long": 15}
		if amount not in length:
			amount = "medium"

		# Game Dictionaries
		game = {"players":  {player.id: 0}, "active": 0, "length": length[amount], "current_question": None, "answered": []}
		self.games[channel.id] = game

		# Waiting for players
		await ctx.send("Game Successfully created. Starting in 20 seconds...")
		#await asyncio.sleep(20)

		# Get questions
		questions = self.get_questions(length[amount])

		# Checks if there is any players to play the game still
		if not self.games[channel.id]["players"]:
			self.games.pop(channel.id)
			return await ctx.send("Abandoning game due to lack of players.")

		# Starts game
		self.games[channel.id]["active"] = 1
		await ctx.send("GAME START")
		await self.game(ctx, channel, questions["results"])

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
					await ctx.send("You have already joined the game. If you want to leave, do `{}trivia leave`".format(self.bot.command_prefix), delete_after=2)
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

	@bot.command()
	async def emojiid(self, ctx, emoji: discord.Emoji = None):
		return await ctx.send(emoji.id)


def setup(Bot):
	Bot.add_cog(Trivia(Bot))