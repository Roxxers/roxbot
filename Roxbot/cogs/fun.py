import random
import re
import discord
import requests
from discord.ext.commands import bot

from Roxbot import checks
from Roxbot.settings import guild_settings
from Roxbot.logging import log


class Fun:
	def __init__(self, bot_client):
		self.bot = bot_client

	@bot.command()
	async def roll(self, ctx, expression):
		"""
		Rolls a die using dice expression format.
		Usage:
			{command_prefix}roll expression
			spaces in expression are ignored
		Example:
			.roll 2d20h1 + 7 # Rolls two D20s takes the highest 1, then adds 7
			.roll #will give brief overview of dice expression format
		"""
		response = ''
		rollVerbose = True
		# sanitise input by removing all spaces, converting to lower case
		expression = expression.lower().replace(' ','')
		# check end of expression for a 'x<number>'
		parts = expression.split('x',1)
		times = 1
		if len(parts) == 2:
			try:
				times = int(parts[1])
				if times < 1:
					times = 1
				if times > 10:
					response += "*Warning:* cannot roll an expression more than 10 times. will roll 10 times rather than {}.\n".format(times)
					times = 10
			except ValueError:
				times = 1
				response += "*Warning:* was unable to resolve how many times this command was meant to run. defaulted to once.\n"
		m=re.findall('(-?)((?:(\d*)d(\d*))|\d+)(r\d*)?([h,l]{1}\d*)?',parts[0])
		if m == []:
			return await ctx.send("Dice expression format:\n\nAn expression can consist of many sub expressions added together and then a multiplier at the end to indicate how many times the expression should be rolled.\n\nSub expressions can be of many types:\n<number> #add this number to the total\nd<sides> #roll a dice with that many sides and add it to the total\n<n>d<sides> #roll n dice. each of those dice have <sides> number of sides, sum all the dice and add to the total\n\tadd r<number> #reroll any rolls below <number>\n\tadd h<number> #only sum the <number> highest rolls rather than all of them\n\tadd l<number> #only sum the <number> lowest rolls rather than all of them\nx<number> #only use at the end. roll the rest of the expression <number> times(max 10)")
		dice = []
		for item in m:
			temp = [0]*5
			temp[0] = 1 if item[0] == '' else -1#if theres a - at the beginning of the sub expression there needs to be a -1 multiplier applied to the sub expression total
			if 'd' in item[1]:#if its a dice/set of dice rather than a number
				if item[2] == '':#if its just a dY rather than an XdY
					temp[1] = 1
					temp[2] = int(item[3])
				else:
					temp[1] = int(item[2])
					if temp[1] > 10 and rollVerbose == True:#if there is a sub expression that involves lots of rolls then turn off verbose mode
						rollVerbose = False
						response += '*Warning:* large number of rolls detected, will not use verbose rolling.\n'
					temp[2] = int(item[3])
			else:
				temp[1] = int(item[1])
				temp[2] = 1
			temp[3] = 0 if item[4] == '' else int(item[4][1:])
			if item[5] == '':
				temp[4] = 0
			else:
				if item[5][0] == 'h':
					temp[4] = int(item[5][1:])
				else:
					temp[4] = -int(item[5][1:])
			dice.append(temp)
		for i in range(times):
			total = 0
			if times > 1:
				response += 'Roll {}: '.format(i+1)
			else:
				response += 'Rolled: '
			for j in range(len(dice)):
				if j != 0 and rollVerbose:
					response += ' + '
				if dice[j][0] == -1 and rollVerbose:
					response += '-'
				if dice[j][2] == 1:
					if rollVerbose:
						response += '{}'.format(dice[j][1])
					total += dice[j][0] * dice[j][1]
				else:
					if rollVerbose:
						response += '('
					temp = []
					for k in range(dice[j][1]):
						t = [0,'']
						t[0] = random.randint(1,dice[j][2])
						t[1] = '{}'.format(t[0])
						if t[0] <= dice[j][3]:
							t[0] = random.randint(1,dice[j][2])
							t[1] += '__{}__'.format(t[0])
						temp.append(t)
					def takeFirst(ele):
						return ele[0]
					if dice[j][4] > 0:
						temp.sort(key=takeFirst, reverse=True)
						for k in range(len(temp)):
							if k >= dice[j][4]:
								temp[k][1] = '~~' + temp[k][1] + '~~'
								temp[k][0] = 0
					if dice[j][4] < 0:
						temp.sort(key=takeFirst)
						for k in range(len(temp)):
							if k >= -dice[j][4]:
								temp[k][1] = '~~' + temp[k][1] + '~~'
								temp[k][0] = 0
					for k in range(len(temp)):
						if rollVerbose:
							response += '{},'.format(temp[k][1])
						total+= dice[j][0] * temp[k][0]
					if rollVerbose:
						response = response[:-1] + ')'
			if rollVerbose:
				response += ' Totaling: {}'.format(total)
			else:
				response += ' Total: {}'.format(total)
			if i < (times-1): response += '\n'
		return await ctx.send(response)

	@checks.isnt_anal()
	@bot.command()
	async def spank(self, ctx, *, user: discord.User = None):
		"""
		Spanks the mentioned user ;)
		Usage:
			{command_prefix}spank @Roxbot#4170
			{command_prefix}spank Roxbot
		"""
		if not user:
			return await ctx.send("You didn't mention someone for me to spank")
		return await ctx.send(":peach: :wave: *{} spanks {}*".format(self.bot.user.name, user.name))

	@checks.isnt_anal()
	@bot.command(aliases=["succ"])
	async def suck(self, ctx, *, user: discord.User = None):
		"""
		Sucks the mentioned user ;)
		Usage:
			{command_prefix}suck @Roxbot#4170
			{command_prefix}suck Roxbot
		"""
		if not user:
			return await ctx.send("You didn't mention someone for me to suck")
		return await ctx.send(":eggplant: :sweat_drops: :tongue: *{} sucks {}*".format(self.bot.user.name, user.name))

	@bot.command()
	async def hug(self, ctx, *, user: discord.User = None):
		"""
		Hugs the mentioned user :3
		Usage:
			{command_prefix}hug @Roxbot#4170
			{command_prefix}hug Roxbott
		"""
		if not user:
			return await ctx.send("You didn't mention someone for me to hug")
		return await ctx.send(":blush: *{} hugs {}*".format(self.bot.user.name, user.name))

	@bot.command(aliases=["headpat"])
	async def pet(self, ctx, *, user: discord.User = None):
		"""
		Gives headpats to the mentioned user :3
		Usage:
			{command_prefix}pet @Roxbot#4170
			{command_prefix}pet Roxbot
		"""
		if not user:
			return await ctx.send("You didn't mention someone for me to headpat")
		return await ctx.send("Nyaa! :3 *{} gives headpats to {}*".format(self.bot.user.name, user.name))

	@bot.command(aliases=["wf", "wr", "husbandorate", "hr", "spousurate", "sr"])
	async def waifurate(self, ctx):
		"""
		Rates the mentioned waifu(s). husbando/spousurate also work.
		Usage:
			{command_prefix}waifurate @user#9999
		This command is in dedicated to Hannah, who suggested this command to me. I hope she's out there, somewhere, getting her waifus rated in peace.
		"""
		mentions = ctx.message.mentions
		if ctx.invoked_with in ["hr", "husbandorate"]:
			waifu = "husbando"
		elif ctx.invoked_with in ["sr", "spousurate"]:
			waifu = "spousu"
		else:
			waifu = "waifu"

		if not mentions:
			return await ctx.send("You didn't mention anyone for me to rate.", delete_after=10)

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
			return await ctx.send("Oh poly {} rating? :smirk: Your combined waifu rating is {}/10. {}".format(waifu, rating, emoji))
		else:
			return await ctx.send("Oh that's your {}? I rate them a {}/10. {}".format(waifu, rating, emoji))

	@bot.command(aliases=["cf"])
	async def coinflip(self, ctx):
		"""Flip a coin"""
		return await ctx.send("The coin landed on {}!".format(random.choice(["heads", "tails"])))

	@bot.command()
	async def aesthetics(self, ctx, *, convert):
		"""Converts text to be more  a e s t h e t i c s"""
		WIDE_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
		WIDE_MAP[0x20] = 0x3000
		converted = str(convert).translate(WIDE_MAP)
		await ctx.send(converted)

		logging = guild_settings.get(ctx.guild).logging
		log_channel = self.bot.get_channel(logging["channel"])
		await log(ctx.guild, log_channel, "aesthetics", User=ctx.author, Argument_Given=convert, Channel=ctx.channel, Channel_Mention=ctx.channel.mention)

	@bot.command(aliases=["ft", "frog"])
	async def frogtips(self, ctx):
		"""RETURNS FROG TIPS FOR HOW TO OPERATE YOUR FROG"""
		endpoint = "https://frog.tips/api/1/tips/"
		croak = requests.get(endpoint)
		tip = random.choice(croak.json()["tips"])
		embed = discord.Embed(title="Frog Tip #{}".format(tip["number"]), description=tip["tip"], colour=discord.Colour(0x4C943D))
		embed.set_author(name="HOW TO OPERATE YOUR FROG")
		embed.set_footer(text="https://frog.tips")
		return await ctx.send(embed=embed)


def setup(bot_client):
	bot_client.add_cog(Fun(bot_client))
