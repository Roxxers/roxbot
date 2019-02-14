# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017-2018 Roxanne Gibson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import asyncio
import datetime
from collections import OrderedDict
from html import unescape
from random import shuffle

import discord
from discord.ext import commands

import roxbot


# TODO: Refactor the game into its own class and have the commands interact with that api.
# Then I can refactor the game into its own lib and then make a cli version.


class Trivia:
	"""
	Roxbot Trivia is a trivia game in *your* discord server. It's heavily inspired by Tower Unite's Trivia mini-game. Uses the [Open Trivia Database](https://opentdb.com) made by PixelTail Games.

	This cog works better if the bot account is in the RoxBot Emoji Server. If it cannot find the emotes it needs, it will default to unicode emoji.
	"""
	def __init__(self, bot_client):
		# Get emoji objects here for the reactions. Basically to speedup the reactions for the game.
		self.bot = bot_client
		self.lengths = {"short": 5, "medium": 10, "long": 15}
		self.games = {}
		self.error_colour = roxbot.EmbedColours.dark_red
		self.trivia_colour = roxbot.EmbedColours.blue
		self.bot.add_listener(self._emoji_vars, "on_ready")

	async def _emoji_vars(self):
		a_emoji = self.bot.get_emoji(419572828854026252) or "🇦"
		b_emoji = self.bot.get_emoji(419572828925329429)  or "🇧"
		c_emoji = self.bot.get_emoji(419572829231775755) or "🇨"
		d_emoji = self.bot.get_emoji(419572828954820620) or "🇩"
		self.correct_emoji = self.bot.get_emoji(421526796392202240) or "✅"
		self.incorrect_emoji = self.bot.get_emoji(421526796379488256) or "❌"
		self.emojis = [a_emoji, b_emoji, c_emoji, d_emoji]

	# Game Functions

	def setup_variables(self, player, channel, *args):
		parser = roxbot.utils.ArgParser()
		parser.add_argument("--mobile", "-m", default=False, action="store_true", dest="mobile")
		parser.add_argument("--solo", "-s", default=False, action="store_true", dest="solo")
		parser.add_argument("--length", "-l", default="medium", type=str, choices=["short", "medium", "long"], dest="length")
		options, unknowns = parser.parse_known_args(args)
		try:
			amount = options.length
		except AttributeError:
			amount = "medium"
		try:
			mobile = options.mobile
		except AttributeError:
			mobile = False
		try:
			solo = options.solo
		except AttributeError:
			solo = False

		# Game Dictionaries
		game = {
			"players":  {player.id: 0},
			"active": 0,
			"length": self.lengths[amount],
			"current_question": None,
			"players_answered": [],
			"correct_users": {},
			"correct_answer": ""
		}
		self.games[channel.id] = game

		kwargs = {"mobile_comp": mobile, "solo": solo}

		return kwargs

	async def get_questions(self, amount=10):
		return await roxbot.http.api_request("https://opentdb.com/api.php?amount={}".format(amount))

	def parse_question(self, question, counter, mobile_comp):
		if mobile_comp:
			embed = "Question {}) **{}**\n\nDifficulty: {} | Category: {} | Time Left: ".format(counter, unescape(question["question"]), question["difficulty"].title(), question["category"])
		else:
			embed = discord.Embed(
				title=unescape(question["question"]),
				colour=discord.Colour(self.trivia_colour),
				description="")

			embed.set_author(name="Question {}".format(counter))
			embed.set_footer(text="Difficulty: {} | Category: {} | Time Left: ".format(question["difficulty"].title(), question["category"]))

		if question["type"] == "boolean":
			# List of possible answers
			choices = ["True", "False"]
			correct = question["correct_answer"]
			# Get index of correct answer
		else:
			# Get possible answers and shuffle them in a list
			incorrect = question["incorrect_answers"]
			correct = question["correct_answer"]
			choices = [correct, *incorrect]
			for x, choice in enumerate(choices):
				choices[x] = unescape(choice)
			shuffle(choices)

		# Then get the index of the correct answer
		correct = choices.index(unescape(correct))
		# Create output
		answers = ""
		for x, choice in enumerate(choices):
			answers += "{} {}\n".format(str(self.emojis[x]), choice)
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

	async def game(self, ctx, channel, questions, *, mobile_comp=False, solo=False):
		# For loop all the questions for the game, Maybe I should move the game dictionary here instead.
		question_count = 1
		for question in questions:
			# Parse question dictionary into something usable
			output, answers, correct = self.parse_question(question, question_count, mobile_comp)
			self.games[channel.id]["correct_answer"] = correct

			# Send a message, add the emoji reactions, then edit in the question to avoid issues with answering before reactions are done.
			if mobile_comp:
				orig = {"content": output}
				sections = output.split("\n")
				sections[1] = answers
				footer = sections[-1]
				sections[-1] = sections[-1] + "20"
				output = "\n".join(sections)
				edit = {"content": output}
			else:
				orig = {"embed": output}
				output.description = answers
				footer = str(output.footer.text)
				output.set_footer(text=output.footer.text+str(20))
				edit = {"embed": output}

			message = await ctx.send(**orig)
			await self.add_question_reactions(message, question)
			await message.edit(**edit)
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
					if mobile_comp:
						sections = output.split("\n")
						sections[-1] = footer + str(20 - (x + 1))
						output = "\n".join(sections)
						edit = {"content": output}
					else:
						output.set_footer(text=footer+str(20 - (x + 1)))
						edit = {"embed": output}
					await message.edit(**edit)
					await asyncio.sleep(1)

			if mobile_comp:
				sections = output.split("\n")
				sections[-1] = footer + "Answered"
				output = "\n".join(sections)
				edit = {"content": output}
			else:
				output.set_footer(text="{} Time Left: Answered".format(footer))
				edit = {"embed": output}
			await message.edit(**edit)

			# Clean up when answers have been submitted
			self.games[channel.id]["current_question"] = None
			await message.clear_reactions()

			# Display Correct answer and calculate and display scores.
			index = self.games[channel.id]["correct_answer"]
			embed = discord.Embed(
				colour=roxbot.EmbedColours.triv_green,
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
		user_in_game = bool(user.id in self.games[channel.id]["players"])
		try:
			reaction_is_on_question = bool(message.id == self.games[channel.id]["current_question"].id)
		except AttributeError:
			if reaction.emoji in self.emojis:
				# This means the question isn't ready
				reaction_is_on_question = False
			else:
				reaction_is_on_question = None

		if channel.id in self.games:
			if user_in_game and reaction_is_on_question:
				if reaction.emoji in self.emojis and user.id not in self.games[channel.id]["players_answered"]:
					self.games[channel.id]["players_answered"].append(user.id)
					if reaction.emoji == self.emojis[self.games[channel.id]["correct_answer"]]:
						self.games[channel.id]["correct_users"][user.id] = time
					return
				else:
					return await message.remove_reaction(reaction, user)
			else:
				if reaction_is_on_question is None:
					return
				return await message.remove_reaction(reaction, user)
		else:
			return

	# Commands

	@commands.guild_only()
	@commands.group(aliases=["tr"], case_insensitive=True)
	async def trivia(self, ctx):
		"""Command group for the Roxbot Trivia game. All interactions with the game are done through this command."""
		if ctx.invoked_subcommand == self.start and ctx.channel.id not in self.games:
			embed = discord.Embed(colour=roxbot.EmbedColours.pink)
			embed.set_footer(text="Roxbot Trivia uses the Open Trivia DB, made and maintained by Pixeltail Games LLC. Find out more at https://opentdb.com/")
			embed.set_image(url="https://i.imgur.com/yhRVl9e.png")
			await ctx.send(embed=embed)
		elif ctx.invoked_subcommand is None:
			await ctx.invoke(self.about)

	@trivia.command()
	async def about(self, ctx):
		"""Displays help in playing Roxbot Trivia. If nothing/an incorrect subcommand is passed to the trivia command, this command is invoked instead."""
		embed = discord.Embed(
			title="About Roxbot Trivia",
			description="Roxbot Trivia is a trivia game in *your* discord server. It's heavily inspired by Tower Unite's Trivia mini-game. Uses the [Open Trivia Database](https://opentdb.com) made by PixelTail Games. To start, just type `{}trivia start`.".format(self.bot.command_prefix),
			colour=roxbot.EmbedColours.pink)
		embed.add_field(name="How to Play", value="Once the game has started, questions will be asked and you will be given 20 seconds to answer them. To answer, react with the corrosponding emoji. Roxbot will only accept your first answer. Score is calculated by how quickly you can answer correctly, so make sure to be as quick as possible to win! Person with the most score at the end wins. Glhf!")
		embed.add_field(name="How does the game end?", value="The game ends once all questions have been answered or if everyone has left the game using the `{}trivia leave` command.".format(self.bot.command_prefix))
		embed.add_field(name="Can I have shorter or longer games?", value="Yes! You can change the length of the game by using the argument `-l or --length` adding short (5 questions), medium (10), or long (15) at the end. `{}trivia start --length short`. The default is medium.".format(self.bot.command_prefix))
		embed.add_field(name="Can I play with friends?", value="Yes! Trivia is best with friends. How else would friendships come to their untimely demise? You can only join a game during the 20 second waiting period after a game is started. Just type `{0}trivia join` and you're in! You can leave a game at anytime (even if its just you) by doing `{0}trivia leave`. If no players are in a game, the game will end and no one will win ;-;".format(self.bot.command_prefix))
		embed.add_field(name="What if I don't want anyone to join my solo game? Waiting is boring!", value="No problem! Just put `-s or --solo` anywhere after `{}trivia start`".format(self.bot.command_prefix))
		embed.add_field(name="I can't read the questions on mobile!", value="Sadly this is an issue with Discord on mobile. To get around this, Roxbot Trivia has a mobile compatible version. Just put `-m or --mobile` anywhere after `{}trivia start`".format(self.bot.command_prefix))
		embed.add_field(name="Can I have a mobile compatible short solo game?", value="Yes, you can use any of the three arguments at once. The Trivia command takes commands just like a cli. Example: `{0}tr start -ms` or `{0}tr start --length long --mobile`".format(self.bot.command_prefix))
		embed.set_footer(text="Roxbot Trivia uses the Open Trivia DB, made and maintained by Pixeltail Games LLC. OpenTDB is licensed under the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) Find out more at [https://opentdb.com/](https://opentdb.com/)")
		embed.set_image(url="https://i.imgur.com/yhRVl9e.png")
		return await ctx.send(embed=embed)

	@commands.guild_only()
	@trivia.command()
	@commands.bot_has_permissions(manage_messages=True)
	async def start(self, ctx, *args):
		"""Starts a trivia game in the channel the command was invoked in. 

		Args: 
			- `--mobile`/`-m` - Launches the game in a mobile compatible mode. In case rich embeds are not readable, especially for Android users.
			- `--solo`/`-s` - Skips waiting for users to join and launches the game immediatly. Useful for users just wanting to play solo.
			- `--length`/`-l` - Takes option for the length of the game. Acceptable options are `short` (5 Questions), `medium` (10), and `long` (15).

		Examples:
			# Start a standard trivia game
			;trivia start

			# Start a mobile compatible solo game of Roxbot Trivia
			;tr start -ms

			# Start a solo short game
			;tr start --solo --length short
		"""
		channel = ctx.channel
		player = ctx.author
		# Check if a game is already running and if so exit.
		if channel.id in self.games:
			# Game active in this channel already
			await ctx.send(embed=discord.Embed(description="A game is already being run in this channel.", colour=self.error_colour))
			await asyncio.sleep(2)
			return await ctx.message.delete()

		# Setup variables and wait for all players to join.
		kwargs = self.setup_variables(player, channel, *args)

		# Get questions
		questions = await self.get_questions(self.games[channel.id]["length"])

		# Waiting for players

		output = "Starting Roxbot Trivia!"
		sleep = 0

		if not kwargs["solo"]:
			output += " Starting in 20 seconds..."
			sleep = 20
		await ctx.send(embed=discord.Embed(description=output, colour=self.trivia_colour))
		await asyncio.sleep(sleep)

		# Checks if there is any players to play the game still
		if not self.games[channel.id]["players"]:
			self.games.pop(channel.id)
			return await ctx.send(embed=discord.Embed(description="Abandoning game due to lack of players.", colour=self.error_colour))

		# Starts game
		self.games[channel.id]["active"] = 1
		await self.game(ctx, channel, questions["results"], **kwargs)

		# Game Ends
		# Some stuff here displaying score
		if self.games[channel.id]["players"]:
			final_scores = []
			for score in self.sort_leaderboard(self.games[channel.id]["players"]).items():
				final_scores.append(score)

			winner = ctx.guild.get_member(final_scores[0][0])
			winning_score = final_scores[0][1]
			winner_text = "{0} won with a score of {1}".format(winner.mention, winning_score)

			if len(final_scores) > 1:
				x = 0
				results_text = "\n\nResults:\n"
				for player in final_scores:
					user = ctx.guild.get_member(player[0])
					if x == 0:
						emoji = "`1st)` 🥇"
					elif x == 1:
						emoji = "`2nd)` 🥈"
					elif x == 2:
						emoji = "`3rd)` 🥉"
					else:
						emoji = "`{}th)` 🎀".format(x+1)
					results_text += "\n {0} {1} - {2}".format(emoji, user.mention, player[1])
					x += 1
			else:
				results_text = ""

			ending_leaderboard = winner_text + results_text
			embed = discord.Embed(description=ending_leaderboard, colour=roxbot.EmbedColours.gold)
			await ctx.send(embed=embed)
		self.games.pop(channel.id)

	@trivia.error
	async def trivia_err(self, ctx, error):
		# TODO: Better before and after invoke systems to deal with variable cleanup
		# This is here to make sure that if an error occurs, the game will be removed from the dict and will safely exit the game, then raise the error like normal.
		try:
			self.games.pop(ctx.channel.id)
			await ctx.send(embed=discord.Embed(description="An error has occured ;-; Exiting the game...", colour=self.error_colour))
			raise error
		except KeyError:
			pass

	@commands.guild_only()
	@trivia.command()
	async def join(self, ctx):
		"""Joins a Trivia game in this channel. The game must be waiting for players to join after a user has executed the `;trivia start` command. You cannot join a game in progress."""
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

	@commands.guild_only()
	@trivia.command()
	async def leave(self, ctx):
		"""Command to leave the game. When invoked, the user leaves the game and their score is removed from the leaderboard. This can be done at any point of the game."""
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

	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@trivia.command()
	async def kick(self, ctx, user: discord.Member):
		"""Mod command to kick users out of the game. Useful if a user is AFK because of the timer on answering questions. Requires Manage Channels permission.

		Example:
			# Kick user called BadTriviaPlayer
			;tr kick @BadTriviaPlayer
		"""
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
