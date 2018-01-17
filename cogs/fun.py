import discord
import random
from discord.ext.commands import bot


class Fun():
	def __init__(self, Bot):
		self.bot = Bot

	@bot.command(pass_context=True)
	async def roll(self, ctx, die):
		"""
		Rolls a die using ndx format.
		Usage:
			{command_prefix}roll ndx
		Example:
			.roll 2d20 # Rolls two D20s
		"""
		# TODO: Change to ndx format
		dice = 0
		if die[0].isdigit():
			if die[1].isdigit() or die[0] == 0:
				return await self.bot.say("I only support multipliers from 1-9")
			multiplier = int(die[0])
		else:
			multiplier = 1
		if die[1].lower() != "d" and die[0].lower() != "d":
			return await self.bot.say("Use the format 'ndx'.")
		options = (4, 6, 8, 10, 12, 20, 100)
		for option in options:
			if die.endswith(str(option)):
				dice = option
		if dice == 0:
			return await self.bot.say("You didn't give a die to use.")

		rolls = []
		if dice == 100:
			step = 10
		else:
			step = 1

		total = 0
		if multiplier > 1:
			for x in range(multiplier):
				rolls.append(random.randrange(step, dice+1, step))
			for r in rolls:
				total += r
			return await self.bot.say("{} rolled **{}**. Totaling **{}**".format(ctx.message.author.mention, rolls, total))
		else:
			roll = random.randrange(step, dice + 1, step)
			return await self.bot.say("{} rolled a **{}**".format(ctx.message.author.mention, roll))

	@bot.command(pass_context=True)
	async def spank(self, ctx, *, user: discord.User = None):
		"""
		Spanks the mentioned user ;)
		Usage:
			{command_prefix}spank @RoxBot#4170
			{command_prefix}spank RoxBot
		"""
		if not user:
			return await self.bot.say("You didn't mention someone for me to spank")
		return await self.bot.say(":peach: :wave: *{} spanks {}*".format(self.bot.user.name, user.name))

	@bot.command(pass_context=True)
	async def suck(self, ctx, *, user: discord.User = None):
		"""
		Sucks the mentioned user ;)
		Usage:
			{command_prefix}suck @RoxBot#4170
			{command_prefix}suck RoxBot
		"""
		if not user:
			return await self.bot.say("You didn't mention someone for me to suck")
		return await self.bot.say(":eggplant: :sweat_drops: :tongue: *{} sucks {}*".format(self.bot.user.name, user.name))

	@bot.command(pass_context=True)
	async def hug(self, ctx, *, user: discord.User = None):
		"""
		Hugs the mentioned user :3
		Usage:
			{command_prefix}hug @RoxBot#4170
			{command_prefix}hug RoxBot
		"""
		if not user:
			return await self.bot.say("You didn't mention someone for me to hug")
		return await self.bot.say(":blush: *{} hugs {}*".format(self.bot.user.name, user.name))

	@bot.command(pass_context=True, aliases=["wf"])
	async def waifurate(self, ctx):
		"""
		Rates the mentioned waifu(s)
		Usage:
			{command_prefix}waifurate @user#9999
		"""
		mentions = ctx.message.mentions
		if not mentions:
			return await self.bot.reply("You didn't mention anyone for me to rate.", delete_after=10)

		rating = random.randrange(1, 11)
		if rating <= 2:
			emoji = ":sob:"
		elif rating <= 4:
			emoji = ":disappointed:"
		elif rating <= 6:
			emoji = ":thinking:"
		elif rating <= 8:
			emoji = ":blush:"
		elif rating == 9:
			emoji = ":kissing_heart:"
		else:
			emoji = ":heart_eyes:"

		if len(mentions) > 1:
			return await self.bot.say("Oh poly waifu rating? :smirk: Your combined waifu rating is {}/10. {}".format(rating, emoji))
		else:
			return await self.bot.say("Oh that's your waifu? I rate them a {}/10. {}".format(rating, emoji))

	@bot.command(pass_context=True, aliases=["cf"])
	async def coinflip(self, ctx):
		"""Flip a coin"""
		return await self.bot.reply("the coin landed on {}!".format(random.choice(["heads", "tails"])))

	@bot.command(pass_context=True)
	async def aesthetics(self, ctx, *convert):
		"""Converts text to be more  a e s t h e t i c s"""
		WIDE_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
		WIDE_MAP[0x20] = 0x3000
		convert = str(' '.join(convert)).translate(WIDE_MAP)
		return await self.bot.say(convert)


def setup(Bot):
	Bot.add_cog(Fun(Bot))