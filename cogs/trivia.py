# -*- coding: utf-8 -*-

import checks
import discord
import asyncio
import requests
import datetime
from html import unescape
from random import shuffle
from collections import OrderedDict
from discord.ext import commands


class Trivia:
	"""
	Trivia is based off the lovely https://opentdb.com made by PixelTail Games.

	This cog requires the bot account to be in the Roxbot Emoji Server to work.
	"""
	def __init__(self, bot_client):
		# Get emoji objects here for the reactions. Basically to speedup the reactions for the game.
		self.bot = bot_client
		a_emoji = self.bot.get_emoji(419572828854026252)
		b_emoji = self.bot.get_emoji(419572828925329429)
		c_emoji = self.bot.get_emoji(419572829231775755)
		d_emoji = self.bot.get_emoji(419572828954820620)
		self.correct_emoji = self.bot.get_emoji(421526796392202240)
		self.incorrect_emoji = self.bot.get_emoji(421526796379488256)
		self.emojis = [a_emoji, b_emoji, c_emoji, d_emoji]
		self.games = {}
		self.error_colour = 0x992d22
		self.trivia_colour = 0x6f90f5

	# Game Functions

	def get_questions(self, amount=10):
		r = requests.get("https://opentdb.com/api.php?amount={}".format(amount))
		return r.json()

	def parse_question(self, question, counter):
		embed = discord.Embed(
			title=unescape(question["question"]),
			colour=discord.Colour(self.trivia_colour),
			description="")

		embed.set_author(name="Question {}".format(counter))
		embed.set_footer(text="Difficulty: {} | Category: {} | Time Left: ".format(question["category"], question["difficulty"].title()))

		if question["type"] == "boolean":
			# List of possible answers
			choices = ["True", "False"]
			correct = question["correct_answer"]
			# Get index of correct answer
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
		return embed, answers, correct

	def calculate_scores(self, channel, time_asked):
		score_added = {}
		for user, time in self.games[channel.id]["correct_users"].items():
			seconds = (time - time_asked).total_seconds()
			seconds = round(seconds, 1)
			if seconds < 10:
				score = (10 - seconds) * 100
				score = int(round(score, -2))
			else:
				score = 50
			score_added[user] = score  # This is just to display the amount of score added to a user
		return score_added

	def sort_leaderboard(self, scores):
		return OrderedDict(sorted(scores.items(), key=lambda x:x[1], reverse=True))

	def display_leaderboard(self, channel, scores_to_add):
		updated_scores = dict(self.games[channel.id]["players"])
		updated_scores = self.sort_leaderboard(updated_scores)
		output_scores = ""
		count = 1
		for scores in updated_scores:
			player = self.bot.get_user(scores)
			if not player:
				player = scores
			if scores in self.games[channel.id]["correct_users"]:
				emoji = self.correct_emoji
			else:
				emoji = self.incorrect_emoji
			output_scores += "{}) {}: {} {}".format(count, player.mention, emoji, updated_scores[scores])
			if scores in scores_to_add:
				output_scores += "(+{})\n".format(scores_to_add[scores])
			else:
				output_scores += "\n"
			count += 1

		return discord.Embed(title="Scores", description=output_scores, colour=discord.Colour(self.trivia_colour))

	async def add_question_reactions(self, message, question):
		if question["type"] == "boolean":
			amount = 2
		else:
			amount = 4
		for x in range(amount):
			await message.add_reaction(self.emojis[x])

	async def game(self, ctx, channel, questions):
		# For loop all the questions for the game, Maybe I should move the game dictionary here instead.
		question_count = 1
		for question in questions:
			# Parse question dictionary into something usable
			output, answers, correct = self.parse_question(question, question_count)
			self.games[channel.id]["correct_answer"] = correct

			# Send a message, add the emoji reactions, then edit in the question to avoid issues with answering before reactions are done.
			message = await ctx.send(embed=output)
			await self.add_question_reactions(message, question)
			output.description = answers
			footer = str(output.footer.text)
			output.set_footer(text=output.footer.text+str(20))
			await message.edit(embed=output)
			time_asked = datetime.datetime.now()

			# Set up variables for checking the question and if it's being answered
			players_yet_to_answer = list(self.games[channel.id]["players"].keys())
			self.games[channel.id]["current_question"] = message

			# Wait for answers
			for x in range(20):
				# Code for checking if there are still players in the game goes here to make sure nothing breaks.
				if not self.games[channel.id]["players"]:
					await message.clear_reactions()
					await ctx.send(embed=discord.Embed(description="Game ending due to lack of players.", colour=self.error_colour))
					return False
				for answered in self.games[channel.id]["players_answered"]:
					if answered in players_yet_to_answer:
						players_yet_to_answer.remove(answered)
				if not players_yet_to_answer:
					break
				else:
					output.set_footer(text=footer+str(20 - (x + 1)))
					await message.edit(embed=output)
					await asyncio.sleep(1)

			output.set_footer(text="")
			await message.edit(embed=output)

			# Clean up when answers have been submitted
			self.games[channel.id]["current_question"] = None
			await message.clear_reactions()

			# Display Correct answer and calculate and display scores.
			index = self.games[channel.id]["correct_answer"]
			embed = discord.Embed(
				colour=discord.Colour(0x1fb600),
				description="Correct answer is {} **{}**".format(
					self.emojis[index],
					unescape(question["correct_answer"])
				)
			)
			await ctx.send(embed=embed)

			# Scores
			scores_to_add = self.calculate_scores(channel, time_asked)
			for user in scores_to_add:
				self.games[channel.id]["players"][user] += scores_to_add[user]

			# Display scores
			await ctx.send(embed=self.display_leaderboard(channel, scores_to_add))

			# Display that
			# Final checks for next question
			self.games[channel.id]["correct_users"] = {}
			self.games[channel.id]["players_answered"] = []
			question_count += 1

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
					return
				else:
					return await message.remove_reaction(reaction, user)
			else:
				return await message.remove_reaction(reaction, user)
		else:
			return

	# Commands

	@commands.group(aliases=["tr"])
	async def trivia(self, ctx):
		"""Command group for the Roxbot Trivia game."""
		if ctx.invoked_subcommand == self.start and not self.games[ctx.channel.id]:
			embed = discord.Embed(colour=0xDEADBF)
			embed.set_footer(text="Roxbot Trivia uses the Open Trivia DB, made and maintained by Pixeltail Games LLC. Find out more at https://opentdb.com/")
			embed.set_image(url="https://i.imgur.com/yhRVl9e.png")
			await ctx.send(embed=embed)
		elif ctx.invoked_subcommand == None:
			await ctx.invoke(self.about)

	@trivia.command()
	async def about(self, ctx):
		"""He;p using the trivia game."""
		embed = discord.Embed(
			title="About Roxbot Trivia",
			description="Roxbot Trivia is a trivia game in *your* discord server. It's heavily inspired by Tower Unite's trivia game. (and even uses the same questions database!) To start, just type `{}trivia start`.".format(self.bot.command_prefix),
			colour=0xDEADBF)
		embed.add_field(name="How to Play", value="Once the game has started, questions will be asked and you will be given 20 seconds to answer them. To answer, react with the corrosponding emoji. Roxbot will only accept your first answer. Score is calculated by how quickly you can answer correctly, so make sure to be as quick as possible to win! Person with the most score at the end wins. Glhf!")
		embed.add_field(name="Can I have shorter or longer games?", value="Yes! You can change the length of the game by adding either short (5 questions) or long (15 questions) at the end of the start command. `{}trivia start short`. The default is 10 and this is the medium option.".format(self.bot.command_prefix))
		embed.add_field(name="Can I play with friends?", value="Yes! Trivia is best with friends. How else would friendships come to their untimely demise? You can only join a game during the 20 second waiting period after a game is started. Just type `{0}trivia join` and you're in! You can leave a game at anytime (even if its just you) by doing `{0}trivia leave`. If no players are in a game, the game will end and no one will win ;-;".format(self.bot.command_prefix))
		embed.set_footer(text="Roxbot Trivia uses the Open Trivia DB, made and maintained by Pixeltail Games LLC. Find out more at https://opentdb.com/")
		embed.set_image(url="https://i.imgur.com/yhRVl9e.png")
		return await ctx.send(embed=embed)

	@trivia.command()
	@commands.bot_has_permissions(manage_messages=True)
	async def start(self, ctx, amount = "medium"):
		"""Starts a trivia game and waits 20 seconds for other people to join."""
		channel = ctx.channel
		player = ctx.author
		# Check if a game is already running and if so exit.
		if channel.id in self.games:
			# Game active in this channel already
			await ctx.send(embed=discord.Embed(description="A game is already being run in this channel.", colour=self.error_colour))
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
		await ctx.send(embed=discord.Embed(description="Starting Roxbot Trivia! Starting in 20 seconds...", colour=self.trivia_colour))
		await asyncio.sleep(20)

		# Get questions
		questions = self.get_questions(length[amount])

		# Checks if there is any players to play the game still
		if not self.games[channel.id]["players"]:
			self.games.pop(channel.id)
			return await ctx.send(embed=discord.Embed(description="Abandoning game due to lack of players.", colour=self.error_colour))

		# Starts game
		self.games[channel.id]["active"] = 1
		await self.game(ctx, channel, questions["results"])

		# Game Ends
		# Some stuff here displaying score
		if self.games[channel.id]["players"]:
			final_scores = self.sort_leaderboard(self.games[channel.id]["players"])
			winner = self.bot.get_user(list(final_scores.keys())[0])
			winning_score = list(final_scores.values())[0]
			embed = discord.Embed(description="{} won with a score of {}".format(winner.mention, winning_score), colour=0xd4af3a)
			await ctx.send(embed=embed)
		self.games.pop(channel.id)

	@trivia.error
	async def trivia_err(self, ctx, error):
		# This is here to make sure that if an error occurs, the game will be removed from the dict and will safely exit the game, then raise the error like normal.
		self.games.pop(ctx.channel.id)
		await ctx.send(embed=discord.Embed(description="An error has occured ;-; Exiting the game...", colour=self.error_colour))
		raise error

	@trivia.command()
	async def join(self, ctx):
		"""Joins a trivia game. Can only be done when a game is waiting for players to join. Not when a game is currently active."""
		channel = ctx.channel
		# Checks if game is in this channel. Then if one isn't active, then if the player has already joined.
		if channel.id in self.games:
			if not self.games[channel.id]["active"]:
				player = ctx.author
				if player.id not in self.games[channel.id]["players"]:
					self.games[channel.id]["players"][player.id] = 0
					return await ctx.send(embed=discord.Embed(description="Player {} joined the game".format(player.mention), colour=self.trivia_colour))
				# Failures
				else:
					return await ctx.send(embed=discord.Embed(description="You have already joined the game. If you want to leave, do `{}trivia leave`".format(self.bot.command_prefix), colour=self.error_colour))
			else:
				return await ctx.send(embed=discord.Embed(description="Game is already in progress.",colour=self.error_colour))
		else:
			return await ctx.send(embed=discord.Embed(description="Game isn't being played here.", colour=self.error_colour))

	@trivia.command()
	async def leave(self, ctx):
		"""Leaves the game in this channel. Can be done anytime in the game."""
		channel = ctx.channel
		player = ctx.author
		# CAN LEAVE:  Game is started or has been activated
		# CANT LEAVE: Game is not active or not in the game
		if channel.id in self.games:
			if player.id in self.games[channel.id]["players"]:
				self.games[channel.id]["players"].pop(player.id)
				await ctx.send(embed=discord.Embed(description="{} has left the game.".format(player.mention), colour=self.trivia_colour))
			else:
				await ctx.send(embed=discord.Embed(description="You are not in this game",
							   colour=self.error_colour))
		else:
			await ctx.send(embed=discord.Embed(description="Game isn't being played here.", colour=self.error_colour))

	@checks.is_admin_or_mod()
	@trivia.command()
	async def kick(self, ctx, user: discord.Member):
		"""Mod command to kick users out of the game. Useful if a user is AFK."""
		channel = ctx.channel
		player = user
		if channel.id in self.games:
			if player.id in self.games[channel.id]["players"]:
				self.games[channel.id]["players"].pop(player.id)
				await ctx.send(embed=discord.Embed(description="{} has been kicked from the game.".format(player.mention), colour=self.trivia_colour))
			else:
				await ctx.send(embed=discord.Embed(description="This user is not in the game",
							   colour=self.error_colour))
		else:
			await ctx.send(embed=discord.Embed(description="Game isn't being played here.", colour=self.error_colour))

def setup(Bot):
	Bot.add_cog(Trivia(Bot))