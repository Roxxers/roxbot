# -*- coding: utf-8 -*-

import discord
import asyncio
import requests
import datetime
from html import unescape
from random import shuffle
from collections import OrderedDict
from discord.ext import commands


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
		self.bot = bot_client
		a_emoji = discord.utils.get(self.bot.emojis, id=419572828854026252)
		b_emoji = discord.utils.get(self.bot.emojis, id=419572828925329429)
		c_emoji = discord.utils.get(self.bot.emojis, id=419572829231775755)
		d_emoji = discord.utils.get(self.bot.emojis, id=419572828954820620)
		self.emojis = [a_emoji, b_emoji, c_emoji, d_emoji]
		self.games = {}

	# Game Functions

	def get_questions(self, amount=10):
		r = requests.get("https://opentdb.com/api.php?amount={}".format(amount))
		return r.json()

	def parse_question(self, question):
		output = "Category: {}\nDifficulty: {}\nQuestion: {}\n".format(question["category"], question["difficulty"],
																	   unescape(question["question"]))
		if question["type"] == "boolean":
			# List of possible answers
			choices = ["True", "False"]
			correct = question["correct_answer"]
			# Get index of correct answer
			correct = choices.index(correct)
			# Create output
			answers = "{} {}\n{} {}".format(str(self.emojis[0]), choices[0], str(self.emojis[1]), choices[1])
		else:
			# Get possible answers and shuffle them in a list
			incorrect = question["incorrect_answers"]
			correct = unescape(question["correct_answer"])
			choices = [incorrect[0], incorrect[1], incorrect[2], correct]
			for answer in choices:
				choices[choices.index(answer)] = unescape(answer)
			shuffle(choices)
			# Then get the index of the correct answer
			correct = choices.index(correct)
			# Create output
			answers = ""
			for x in range(len(choices)):
				answers += "{} {}\n".format(str(self.emojis[x]), choices[x])
		return output, answers, correct

	def calculate_scores(self, channel, message):
		score_added = {}
		for user, time in self.games[channel.id]["correct_users"].items():
			seconds = (time - message.edited_at).total_seconds()
			seconds = round(seconds, 1)
			if seconds < 10:
				score = (10 - seconds) * 100
				score = int(round(score, -2))
			else:
				score = 50
			score_added[user] = score  # This is just to display the amount of score added to a user
		return score_added

	async def add_question_reactions(self, message, question):
		if question["type"] == "boolean":
			amount = 2
		else:
			amount = 4
		for x in range(amount):
			await message.add_reaction(self.emojis[x])

	async def game(self, ctx, channel, questions):
		# For loop all the questions for the game, Maybe I should move the game dictionary here instead.
		# TODO: Defo needs some cleaning up
		for question in questions:
			# Parse question dictionary into something usable
			output, answers, correct = self.parse_question(question)
			self.games[channel.id]["correct_answer"] = correct

			# Send a message, add the emoji reactions, then edit in the question to avoid issues with answering before reactions are done.
			message = await ctx.send(output)
			await self.add_question_reactions(message, question)
			await message.edit(content=output+answers)

			# Set up variables for checking the question and if it's being answered
			players_yet_to_answer = list(self.games[channel.id]["players"].keys())
			self.games[channel.id]["current_question"] = message
			# Wait for answers
			for x in range(20):
				for answered in self.games[channel.id]["players_answered"]:
					if answered in players_yet_to_answer:
						players_yet_to_answer.remove(answered)
				if not players_yet_to_answer:
					break
				else:
					await asyncio.sleep(1)

			# Code for checking if there are still players in the game goes here to make sure nothing breaks.
			if not self.games[channel.id]["players"]:
				await message.clear_reactions()
				await ctx.send("No more players to play the game")
				break

			# Clean up when answers have been submitted
			self.games[channel.id]["current_question"] = None
			await message.clear_reactions()

			# Display Correct answer and calculate and display scores.
			index = self.games[channel.id]["correct_answer"]
			await ctx.send("Correct Answer is {} '{}'".format(self.emojis[index], unescape(question["correct_answer"])))

			# Scores
			scores_to_add = self.calculate_scores(channel, message)
			for user in scores_to_add:
				self.games[channel.id]["players"][user] += scores_to_add[user]

			# Display scores
			updated_scores = dict(self.games[channel.id]["players"])
			for player in updated_scores:
				if player in self.games[channel.id]["correct_users"]:
					updated_scores[player] = str(updated_scores[player]) + " (+{})".format(scores_to_add[player])
				else:
					updated_scores[player] = str(updated_scores[player])
			updated_scores = OrderedDict(sorted(updated_scores.items(), key=lambda kv: kv))
			output_scores = ""
			for scores in updated_scores:
				output_scores += "{}: {}\n".format(scores, updated_scores[scores])

			await ctx.send(output_scores)

			# Display that
			# Final checks for next question
			self.games[channel.id]["correct_users"] = {}
			self.games[channel.id]["players_answered"] = []


		# Game Ends
		# Some stuff here displaying score
		self.games.pop(channel.id)
		await ctx.send("GAME END")

	# Discord Events

	async def on_reaction_add(self, reaction, user):
		"""Logic for answering a question"""
		time = datetime.datetime.now()
		if user == self.bot.user:
			return

		channel = reaction.message.channel
		message = reaction.message

		if channel.id in self.games:
			if user.id in self.games[channel.id]["players"] and message.id == self.games[channel.id]["current_question"].id:
				if reaction.emoji in self.emojis and user.id not in self.games[channel.id]["players_answered"]:
					self.games[channel.id]["players_answered"].append(user.id)
					if reaction.emoji == self.emojis[self.games[channel.id]["correct_answer"]]:
						self.games[channel.id]["correct_users"][user.id] = time
					return  # Maybe add something removing reactions if they are not allowed.
				else:
					return await message.remove_reaction(reaction, user)
			else:
				return await message.remove_reaction(reaction, user)
		else:
			return

	# Commands

	@commands.group(aliases=["tr"])
	async def trivia(self, ctx):
		pass

	@trivia.command()
	@commands.bot_has_permissions(manage_messages=True)
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
		game = {
			"players":  {player.id: 0},
			"active": 0,
			"length": length[amount],
			"current_question": None,
			"players_answered": [],
			"correct_users": {},
			"correct_answer": ""
		}
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


def setup(Bot):
	Bot.add_cog(Trivia(Bot))