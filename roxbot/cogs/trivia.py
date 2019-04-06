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


import enum
import asyncio
import datetime
from collections import OrderedDict
from html import unescape
from random import shuffle

import discord
from discord.ext import commands

import roxbot


class TriviaLengths(enum.IntEnum):
    short = 5
    medium = 10
    long = 15


class Question:
    """
    Question Object to aide the trivia game. Handles accessing the parts of the question.
    """
    def __init__(self, question, index, emojis, mobile_compatible=False):
        self.question = unescape(question["question"])
        self.question_index = index
        self.mobile_compatible = mobile_compatible
        self.type = unescape(question["type"])
        self.category = unescape(question["category"])
        self.difficulty = unescape(question["difficulty"]).title()
        self.correct_answer = unescape(question["correct_answer"])
        self.emojis = emojis
        if self.type == "boolean":
            self.answers = ["True", "False"]
        else:
            self.answers = [unescape(answer) for answer in question["incorrect_answers"]]
            self.answers.append(self.correct_answer)
            shuffle(self.answers)
        self.correct_answer_index = self.answers.index(self.correct_answer)
        self.payload = self.gen_question_embed()
        self.answers_str = self.format_answers()

    def gen_question_embed(self):
        if self.mobile_compatible:
            msg = "Question {0.question_index}) **{0.question}**\n\nDifficulty: {0.difficulty} | Category: {0.category} | Time Left: ".format(self)
            payload = {"content": msg}
        else:
            embed = discord.Embed(
                title=self.question,
                colour=discord.Colour(roxbot.EmbedColours.blue),
                description="")

            embed.set_author(name="Question {}".format(self.question_index))
            embed.set_footer(text="Difficulty: {0.difficulty} | Category: {0.category} | Time Left: ".format(self))
            payload = {"embed": embed}
        return payload

    def format_answers(self):
        formatted = ""
        for x, answer in enumerate(self.answers):
            formatted += "{} {}\n".format(self.emojis[x], answer)
        return formatted

    def insert_answers(self, message):
        if self.mobile_compatible:
            sections = message.content.split("\n")
            sections[1] = self.answers_str
            sections[-1] = sections[-1] + " 20"
            output = "\n".join(sections)
            edit = {"content": output}
        else:
            embed = message.embeds[0]
            embed.description = self.answers_str
            embed.set_footer(text=embed.footer.text + " " + str(20))
            edit = {"embed": embed}
        return edit

    async def add_question_reactions(self, message):
        if self.type == "boolean":
            amount = 2
        else:
            amount = 4
        for x in range(amount):
            await message.add_reaction(self.emojis[x])


class Leaderboard:
    def __init__(self, player_id):
        self.scores = {player_id: 0}
        self.diffs = {player_id: 0}

    @property
    def players(self):
        return list(self.scores.keys())

    @property
    def leaderboard(self):
        return self.sort_leaderboard()

    @property
    def ranks_from_scores(self):
        """sorted_scores: a list of tuples (player_id, score), sorted by score DESCENDING
           return a mapping of object IDs to ranks
        """
        rank = 0
        ranks = {}
        previous_score = None
        for index, (player_id, score) in enumerate(list(self.leaderboard.items())):
            if score != previous_score:
                previous_score = score
                rank = index + 1
            ranks[player_id] = rank
        return ranks


    def add_player(self, player_id):
        self.scores[player_id] = 0
        self.diffs[player_id] = 0

    def remove_player(self, player_id):
        self.scores.pop(player_id)
        self.diffs.pop(player_id)

    def calulate_score(self, timer_start, time_answered):
        seconds = (time_answered - timer_start).total_seconds()
        # Amount of seconds is changed to make the time calculated more accurate to the timer in the game
        seconds = seconds - (seconds * 0.2)
        seconds = round(seconds, 1)
        if seconds < 10:
            score = (10 - seconds) * 100
            score = int(round(score, -2))
        else:
            score = 50
        return score

    def add_score(self, player_id, score_to_add):
        self.scores[player_id] += score_to_add
        self.diffs[player_id] = score_to_add

    def sort_leaderboard(self):
        return OrderedDict(sorted(self.scores.items(), key=lambda x: x[1], reverse=True))

    def flush_diffs(self):
        for player in self.diffs:
            self.diffs[player] = 0


class TriviaGame:
    """
    Trivia Game Object
    Handles all interactions and logic with the game itself. Providing a quasi api for other functions to call on.
    bot: discord.ext.commands.Bot object
    ctx: discord.ext.commands.Context object for the game to use
    args: arguments given to the game to setup its variables
    """
    def __init__(self, bot, ctx, *args):
        self.active = False
        self.ctx = ctx
        self.bot = bot
        parsed = self.parse_args(*args)
        self.solo = parsed["solo"]
        self.mobile_compatible = parsed["mobile_compatible"]
        self.length = parsed["length"]
        self.leaderboard = Leaderboard(ctx.author.id)
        self.players_answered = []
        self.time_asked = None
        self.current_question = None
        self.current_question_message = None
        self.question_in_progress = False
        self.start_message = None

        a_emoji = bot.get_emoji(419572828854026252) or "🇦"
        b_emoji = bot.get_emoji(419572828925329429)  or "🇧"
        c_emoji = bot.get_emoji(419572829231775755) or "🇨"
        d_emoji = bot.get_emoji(419572828954820620) or "🇩"
        self.correct_emoji = bot.get_emoji(421526796392202240) or "✅"
        self.incorrect_emoji = bot.get_emoji(421526796379488256) or "❌"
        self.emojis = [a_emoji, b_emoji, c_emoji, d_emoji]
        self.error_colour = roxbot.EmbedColours.dark_red
        self.trivia_colour = roxbot.EmbedColours.blue

    async def get_questions(self, amount=10):
        """
        API call to the OpenTDB
        amount: positive int, amount of questions wanted to be returned [optional, default 10]
        returns a list of Question objects
        """
        questions = await roxbot.http.api_request("https://opentdb.com/api.php?amount={}".format(amount))
        try:
            if questions["response_code"] == 0:
                return [Question(question, x+1, self.emojis, mobile_compatible=self.mobile_compatible) for x, question in enumerate(questions["results"])]
            else:
                raise commands.CommandError("Cannot get Trivia questions.")
        except KeyError:
            raise commands.CommandError("Cannot get Trivia questions.")

    def parse_args(self, *args):
        """
        parses given arguments given to the game. Uses a modified ArgParser so this doesn't exit the program on fail.
        :param args: list of args
        :return: dict of the results of the parsing.
        """
        parser = roxbot.utils.ArgParser()
        parser.add_argument("--mobile", "-m", default=False, action="store_true", dest="mobile")
        parser.add_argument("--solo", "-s", default=False, action="store_true", dest="solo")
        parser.add_argument("--length", "-l", default="medium", type=str, choices=["short", "medium", "long"], dest="length")
        try:
            options, unknowns = parser.parse_known_args(args)
        except TypeError:
            raise commands.BadArgument("Error in arguments given. Could not parse: {}".format(args))
        try:
            if options.length == "short":
                length = TriviaLengths.short
            elif options.length == "long":
                length = TriviaLengths.long
            else:
                length = TriviaLengths.medium
        except AttributeError:
            length = TriviaLengths.medium

        try:
            mobile = options.mobile
        except AttributeError:
            mobile = False

        try:
            solo = options.solo
        except AttributeError:
            solo = False

        if mobile:
            # Deprecation warning
            embed = discord.Embed(description="Mobile Compatibility is deprecated and will no longer be supported.",
                                  colour=roxbot.EmbedColours.orange)
            embed.set_footer(text="It's no longer is required as the Android app now renders embeds correctly.")
            self.bot.loop.create_task(self.ctx.send(embed=embed))

        return {"mobile_compatible": mobile, "solo": solo, "length": length}

    def edit_question_counter(self, message, finished=False, time=0):
        """
        helper function to edit the question message so it displays a timer.
        :param message: discord.Message object
        :param finished: bool if the counter has finished [optional]
        :param time: the amount of time elapsed
        :return:
        """
        if finished:
            time_str = " Finished"
        else:
            time_str = " " + str(20 - (time + 1))
        if self.mobile_compatible:
            sections = message.content.split("\n")
            footer = " ".join(sections[-1].split()[:-1])
            sections[-1] = footer + time_str
            output = "\n".join(sections)
            return {"content": output}
        else:
            footer = " ".join(message.embeds[0].footer.text.split()[:-1])

            message.embeds[0].set_footer(text=footer + " " + time_str)
            return {"embed": message.embeds[0]}

    async def start(self):
        """
        Sets up a game in the channel in self.ctx.
        :return:
        """
        self.questions = await self.get_questions(self.length)
        # TODO: Add a list that shows the current players in the game, then remove messages to join the game as players join to have like a growning list

        if self.solo:
            embed = discord.Embed(description="Starting Roxbot Trivia!", colour=self.trivia_colour)
            sleep = 0
        else:
            embed = discord.Embed(description="Starting Roxbot Trivia! Starting in 20 seconds...", colour=self.trivia_colour)
            embed.description += "\n\nPress the {} to join, the {} to leave.".format(self.correct_emoji, self.incorrect_emoji)
            sleep = 20

        self.start_message = await self.ctx.send(embed=embed)
        if not self.solo:
            await self.start_message.add_reaction(self.correct_emoji)
            await self.start_message.add_reaction(self.incorrect_emoji)
            await asyncio.sleep(sleep)
            await self.start_message.clear_reactions()

        # Checks if there is any players to play the game still
        if not self.leaderboard.players:
            return await self.ctx.send(embed=discord.Embed(description="Abandoning game due to lack of players.", colour=self.error_colour))

        # Starts game
        self.active = True
        await self.game()
        await self.end_screen()

    async def game(self):
        # Loop Questions

            # Send a message, add the emoji reactions, then edit in the question to avoid issues with answering before reactions are done.

            # question_mesg = await ctx.send(**Question.payload)

            # add question reactions

            # edit = Question.insert_answers(question_mesg)

            # get current_datetime

            # get a list of players that haven't answered

            # wait for answers
            # During wait keep checking in intervals if a player has answered
                # Exit if no players
                # Visabily increment timer
            # Players answer via a different function where it will note a player has answered and the datetime

            # Show the question as answered

            # Clear reactions on message

            # Show correct answer

            # Calculate and show leaderboard w/ score changes

        # End of loop, show final leaderboard and winner

        for index, question in enumerate(self.questions):
            self.current_question = question
            timer = 0
            message = await self.ctx.send(**question.payload)
            self.current_question_message = message
            await question.add_question_reactions(message)
            await message.edit(**question.insert_answers(message))
            self.time_asked = datetime.datetime.now()
            self.question_in_progress = True

            freq = 10
            for num_cycles in range(20*freq):
                if not self.leaderboard.players:
                    await message.clear_reactions()
                    return await self.ctx.send(embed=discord.Embed(description="Game ending due to lack of players.", colour=self.error_colour))
                if len(self.players_answered) == len(self.leaderboard.players):
                    break
                else:
                    timer += 1000/freq
                    if timer % 1000 == 0:
                        # Sleep is separated from message edit because time taken to edit the message is about the time
                        # for a full sleep. Therefore this should yield a more accurate timer.
                        await message.edit(**self.edit_question_counter(message, time=int(num_cycles / freq)))
                    else:
                        await asyncio.sleep(0.1)

            self.question_in_progress = False
            await message.edit(**self.edit_question_counter(message, finished=True))
            await message.clear_reactions()

            # Display Correct answer and calculate and display scores.
            embed = discord.Embed(
                colour=roxbot.EmbedColours.triv_green,
                description="Correct answer is {} **{}**".format(self.emojis[question.correct_answer_index], question.correct_answer)
            )
            await self.ctx.send(embed=embed)

            # Display scores
            leaderboard = self.leaderboard.sort_leaderboard()
            await self.ctx.send(embed=self.generate_leaderboard(leaderboard))

            # Clean Variables
            self.players_answered = []
            self.leaderboard.flush_diffs()
            self.current_question = None
            self.current_question_message = None

            # Wait for next question, if not last question
            wait_time = 3
            if (index + 1) < len(self.questions):
                embed = discord.Embed(description="Next question in: 3", colour=roxbot.EmbedColours.blue)
                message = await self.ctx.send(embed=embed)
                await asyncio.sleep(0.8)
                for x in range(wait_time-1):
                    embed.description = " ".join(embed.description.split()[:-1]) + " " + str(wait_time-1-x)
                    await message.edit(embed=embed)
                    # This is to counter around the average edit times from discord server's I recorded
                    await asyncio.sleep(0.8)
                await message.delete()

    async def end_screen(self):
        if self.leaderboard.players:
            final_scores = []
            for score in self.leaderboard.sort_leaderboard().items():
                final_scores.append(score)

            ranks = self.leaderboard.ranks_from_scores

            winner = self.ctx.guild.get_member(final_scores[0][0])
            winning_score = final_scores[0][1]
            winner_text = "{0} won with a score of {1}".format(winner.mention, winning_score)

            if len(final_scores) > 1:
                if final_scores[0][1] == final_scores[1][1]:
                    # This means there is a tie of any size for first place
                    winner_text = "It's a tie! With a score of {}...".format(final_scores[0][1])
                results_text = "\n\nResults:\n"
                prev_pos = 0
                for player in final_scores:
                    user = self.ctx.guild.get_member(player[0])

                    if ranks[user.id] == 1:
                        pos = "`1st)` "
                        emoji = "🥇"
                    elif ranks[user.id] == 2:
                        pos = "`2nd)` "
                        emoji = "🥈"
                    elif ranks[user.id] == 3:
                        pos = "`3rd)` "
                        emoji = "🥉"
                    else:
                        pos = "`{}th)` ".format(ranks[user.id])
                        emoji = "🎀"

                    if ranks[user.id] == prev_pos:
                        pos = "`---)` "

                    prefix = pos + emoji
                    prev_pos = ranks[user.id]
                    results_text += "\n {0} {1} - {2}".format(prefix, user.mention, player[1])
            else:
                results_text = ""

            ending_leaderboard = winner_text + results_text
            embed = discord.Embed(description=ending_leaderboard, colour=roxbot.EmbedColours.gold)
            await self.ctx.send(embed=embed)

    def player_answer(self, player_id, emoji_choice, time_answered):
        try:
            if player_id not in self.players_answered:
                if self.emojis.index(emoji_choice) == self.current_question.correct_answer_index:
                    score = self.leaderboard.calulate_score(self.time_asked, time_answered)
                    self.leaderboard.add_score(player_id, score)
                self.players_answered.append(player_id)
        except ValueError:
            pass

    def generate_leaderboard(self, leaderboard):
        output_scores = ""
        ranks = self.leaderboard.ranks_from_scores
        prev_pos = 0
        for player_id in leaderboard:
            player = self.bot.get_user(player_id)
            if not player:
                player = player_id
            if self.leaderboard.diffs[player_id] != 0:
                emoji = self.correct_emoji
            else:
                emoji = self.incorrect_emoji

            if ranks[player_id] == prev_pos:
                pos = "-"
            else:
                pos = ranks[player_id]

            prev_pos = ranks[player_id]
            output_scores += "{}) {}: {} {}".format(pos, player.mention, emoji, self.leaderboard.scores[player_id])
            output_scores += "(+{})\n".format(self.leaderboard.diffs[player_id])

        return discord.Embed(title="Leaderboard", description=output_scores, colour=discord.Colour(self.trivia_colour))

    async def add_player(self, player):
        if not self.active:
            if player.id not in self.leaderboard.players:
                self.leaderboard.add_player(player.id)
                embed = discord.Embed(description="Player {} joined the game".format(player.mention), colour=self.trivia_colour)
                return await self.ctx.send(embed=embed)
            else:
                embed = discord.Embed(description="{}. you have already joined the game. If you want to leave, type `{}trivia leave`".format(player, self.bot.command_prefix), colour=self.error_colour)
                return await self.ctx.send(embed=embed)
        else:
            return await self.ctx.send(embed=discord.Embed(description="Game is already in progress.", colour=self.error_colour))

    async def remove_player(self, player):
        if player.id in self.leaderboard.players:
            self.leaderboard.remove_player(player.id)
            await self.ctx.send(embed=discord.Embed(description="{} has left the game.".format(player.mention), colour=self.trivia_colour))
        else:
            await self.ctx.send(embed=discord.Embed(description="You are not in this game", colour=self.error_colour))


class Trivia(commands.Cog):
    """
    Roxbot Trivia is a trivia game in *your* discord server. It's heavily inspired by Tower Unite's Trivia mini-game. Uses the [Open Trivia Database](https://opentdb.com) made by PixelTail Games.

    This cog works better if the bot account is in the RoxBot Emoji Server. If it cannot find the emotes it needs, it will default to unicode emoji.
    """
    def __init__(self, bot):
        # Get emoji objects here for the reactions. Basically to speedup the reactions for the game.
        self.bot = bot
        self.lengths = {"short": 5, "medium": 10, "long": 15}
        self.games = {}
        self.error_colour = roxbot.EmbedColours.dark_red
        self.trivia_colour = roxbot.EmbedColours.blue

    # Discord Events

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Logic for answering a question"""

        channel = reaction.message.channel

        if user == self.bot.user: return
        if channel.id not in self.games:
            return
        else:
            game = self.games[channel.id]

        if not game.active:
            return await self.reaction_game_join_leave(reaction, user)
        else:
            return await self.reaction_to_question(reaction, user)

    async def reaction_game_join_leave(self, reaction, user):
        game = self.games[reaction.message.channel.id]
        if reaction.emoji == game.correct_emoji:
            await game.add_player(user)
        elif reaction.emoji == game.incorrect_emoji:
            await game.remove_player(user)
        await reaction.message.remove_reaction(reaction, user)

    async def reaction_to_question(self, reaction, user):
        time = datetime.datetime.now()
        game = self.games[reaction.message.channel.id]
        accepting_answers = game.question_in_progress and game.current_question_message.id == reaction.message.id
        user_in_game = bool(user.id in game.leaderboard.players)

        if user_in_game and accepting_answers:
            if reaction.emoji in game.emojis:
                game.player_answer(user.id, reaction.emoji, time)
            else:
                return await reaction.message.remove_reaction(reaction, user)
        else:
            return await reaction.message.remove_reaction(reaction, user)


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
            raise commands.CommandNotFound("Subcommand '{}' does not exist.".format(ctx.subcommand_passed))

    @trivia.command()
    async def about(self, ctx):
        """Displays help in playing Roxbot Trivia. If nothing/an incorrect subcommand is passed to the trivia command, this command is invoked instead."""
        # TODO: Edit about to include info about the new method of joining
        # TODO: Remove mobile stuff as its deprecated
        embed = discord.Embed(
            title="About Roxbot Trivia",
            description="Roxbot Trivia is a trivia game in *your* discord server. It's heavily inspired by Tower Unite's Trivia mini-game. Uses the [Open Trivia Database](https://opentdb.com) made by PixelTail Games. To start, just type `{}trivia start`.".format(self.bot.command_prefix),
            colour=roxbot.EmbedColours.pink)
        embed.add_field(name="How to Play", value="Once the game has started, questions will be asked and you will be given 20 seconds to answer them. To answer, react with the corrosponding emoji. Roxbot will only accept your first answer. Score is calculated by how quickly you can answer correctly, so make sure to be as quick as possible to win! Person with the most score at the end wins. Glhf!")
        embed.add_field(name="How does the game end?", value="The game ends once all questions have been answered or if everyone has left the game using the `{}trivia leave` command.".format(self.bot.command_prefix))
        embed.add_field(name="Can I have shorter or longer games?", value="Yes! You can change the length of the game by using the argument `-l or --length` adding short (5 questions), medium (10), or long (15) at the end. `{}trivia start --length short`. The default is medium.".format(self.bot.command_prefix))
        embed.add_field(name="Can I play with friends?", value="Yes! Trivia is best with friends. How else would friendships come to their untimely demise? You can only join a game during the 20 second waiting period after a game is started. Just type `{0}trivia join` and you're in! You can leave a game at anytime (even if its just you) by doing `{0}trivia leave`. If no players are in a game, the game will end and no one will win ;-;".format(self.bot.command_prefix))
        embed.add_field(name="What if I don't want anyone to join my solo game? Waiting is boring!", value="No problem! Just put `-s or --solo` anywhere after `{}trivia start`".format(self.bot.command_prefix))
        embed.add_field(name="Can I have a short solo game?", value="Yes, you can use both arguments at once. The Trivia command takes commands just like a cli. Example: `;tr start -sl short` or `;tr start --solo --length long`")
        embed.set_footer(text="Roxbot Trivia uses the Open Trivia DB, made and maintained by Pixeltail Games LLC. OpenTDB is licensed under the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) Find out more at [https://opentdb.com/](https://opentdb.com/)")
        embed.set_image(url="https://i.imgur.com/yhRVl9e.png")
        return await ctx.send(embed=embed)

    @commands.guild_only()
    @trivia.command()
    @commands.bot_has_permissions(manage_messages=True)
    async def start(self, ctx, *args):
        """Starts a trivia game in the channel the command was invoked in.

        Args:
            - `--solo`/`-s` - Skips waiting for users to join and launches the game immediatly. Useful for users just wanting to play solo.
            - `--length`/`-l` - Takes option for the length of the game. Acceptable options are `short` (5 Questions), `medium` (10), and `long` (15).

        Examples:
            # Start a standard trivia game
            ;trivia start

            # Start a solo game of Roxbot Trivia
            ;tr start -s

            # Start a solo short game
            ;tr start --solo --length short
        """
        channel = ctx.channel
        # Check if a game is already running and if so exit.
        if channel.id in self.games:
            # Game active in this channel already
            await ctx.send(embed=discord.Embed(description="A game is already being run in this channel.", colour=self.error_colour))
            await asyncio.sleep(2)
            return await ctx.message.delete()

        game = TriviaGame(self.bot, ctx, *args)
        self.games[ctx.channel.id] = game
        await game.start()
        self.games.pop(channel.id)

    @start.error
    async def trivia_err(self, ctx, error):
        # This is here to make sure that if an error occurs, the game will be removed from the dict and will safely exit the game, then raise the error like normal.
        try:
            self.games.pop(ctx.channel.id)
            await ctx.send(embed=discord.Embed(description="An error has occured ;-; Exiting the game...\n{}".format(error), colour=self.error_colour))
        except KeyError:
            pass

    @commands.guild_only()
    @trivia.command()
    async def join(self, ctx):
        """Joins a Trivia game in this channel. The game must be waiting for players to join after a user has executed the `;trivia start` command. You cannot join a game in progress."""
        channel = ctx.channel
        # Checks if game is in this channel. Then if one isn't active, then if the player has already joined.
        if channel.id in self.games:
            await self.games[channel.id].add_player(ctx.author)
            await ctx.message.delete()
        else:
            await ctx.send(embed=discord.Embed(description="Game isn't being played here.", colour=self.error_colour))

    @commands.guild_only()
    @trivia.command()
    async def leave(self, ctx):
        """Command to leave the game. When invoked, the user leaves the game and their score is removed from the leaderboard. This can be done at any point of the game."""
        channel = ctx.channel
        player = ctx.author
        # CAN LEAVE:  Game is started or has been activated
        # CANT LEAVE: Game is not active or not in the game
        if channel.id in self.games:
            await self.games[channel.id].remove_player(player)
            await ctx.message.delete()
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
            await self.games[channel.id].remove_player(player)
        else:
            await ctx.send(embed=discord.Embed(description="Game isn't being played here.", colour=self.error_colour))


def setup(bot):
    bot.add_cog(Trivia(bot))
