import discord
import random
import checks
import requests
from discord.ext.commands import bot


class Fun:
	def __init__(self, bot_client):
		self.bot = bot_client

	@bot.command()
	async def roll(self, ctx, expression):
		"""
		Rolls a die using ndx like format.
		Usage:
			{command_prefix}roll expression
			spaces in expression are ignored
		Example:
			.roll 2d20h1 + 7 # Rolls two D20s takes the highest 1, then adds 7
		"""
		times = 1
		# sanitise input by removing all spaces, converting to lower case, and making all terms separate with a + even if negative
		expression = expression.lower().replace(' ','').replace('-','+-')
		# check end of expression for a 'x<number>'
		parts = expression.split('x',1)
		if len(parts) == 2:
			try:
				times = int(parts[1])
			except ValueError:
				times = 1##might want to add error report to user to say its not valid so they dont make the mistake again
		dice = parts[0].split('+')
		#each element of dice should be one of:
		#	<number>
		#	d<number(positive)>
		#	<number>d<number(positive)>[selector][number(positive)]
		exp = []
		for i in range(len(dice)):
			temp = dice[i].split('d',1)
			if temp[0]=='':
				temp[0] = 1
			temp=temp+temp[1].split('l',1)
			del temp[1]
			if len(temp)==3:
				temp[2] = '-' + temp[2]
			else:
				temp = temp + temp[1].split('h',1)
				del temp[1]
			for j in range(len(temp)):
				try:
					temp[j] = int(temp[j])
				except ValueError:
					##big error but its hard to tell what caused it
					return await ctx.send("Something went wrong. check your formatting, or stop putting words in the expression")
			dice[i] = temp
		response = ''
		for i in range(times):
			if times > 1:
				response += 'roll {}: '.format(i)
			total = 0
			for die in dice:
				if len(die) == 1:
					total += die[0]
					if die[0] >= 0:
						response += '+'
					response += '{}'.format(die[0])
				elif len(die) == 2:
					if die[0] >= 0:
						response += '+('
					else:
						response += '-('
					for j in range(abs(die[0])):
						temp = random.randint(1,die[1])
						response += '{},'.format(temp)
						if die[0] >= 0:
							total += temp
						else:
							total -= temp
					response = response[:-1]+')'
				elif len(die) == 3:
					mul=0
					if die[0] >= 0:
						response += '+('
						mul= 1
					else:
						response += '-('
						mul= -1
					temp=[]
					for j in range(abs(die[0])):
						temp.append(random.randint(1,die[1]))
					temp.sort(reverse=True)
					for j in range(abs(die[0])):
						if die[2] > 0:
							if j < die[2]:
								response += '{},'.format(temp[j])
								total += mul * temp[j]
							else:
								response += '~~{}~~,'.format(temp[j])
						else:
							if j >= abs(die[0])+die[2]:
								response += '{},'.format(temp[j])
								total += mul * temp[j]
							else:
								response += '~~{}~~,'.format(temp[j])
					response = response[:-1]+')'
				else:
					##something bizarre happened
					return await ctx.send("Out of cheese error. Please reboot universe")
			response += ' total:{}'.format(total)
			if i < (times-1):
				response += '\n'
		return await ctx.send(response)

	@checks.isnt_anal()
	@bot.command()
	async def spank(self, ctx, *, user: discord.User = None):
		"""
		Spanks the mentioned user ;)
		Usage:
			{command_prefix}spank @Roxbot_client#4170
			{command_prefix}spank Roxbot_client
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
			{command_prefix}suck @Roxbot_client#4170
			{command_prefix}suck Roxbot_client
		"""
		if not user:
			return await ctx.send("You didn't mention someone for me to suck")
		return await ctx.send(":eggplant: :sweat_drops: :tongue: *{} sucks {}*".format(self.bot.user.name, user.name))

	@bot.command()
	async def hug(self, ctx, *, user: discord.User = None):
		"""
		Hugs the mentioned user :3
		Usage:
			{command_prefix}hug @Roxbot_client#4170
			{command_prefix}hug Roxbot_client
		"""
		if not user:
			return await ctx.send("You didn't mention someone for me to hug")
		return await ctx.send(":blush: *{} hugs {}*".format(self.bot.user.name, user.name))

	@bot.command(aliases=["wf"])
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
			return await ctx.send("Oh poly waifu rating? :smirk: Your combined waifu rating is {}/10. {}".format(rating, emoji))
		else:
			return await ctx.send("Oh that's your waifu? I rate them a {}/10. {}".format(rating, emoji))

	@bot.command(aliases=["cf"])
	async def coinflip(self, ctx):
		"""Flip a coin"""
		return await ctx.send("The coin landed on {}!".format(random.choice(["heads", "tails"])))

	@bot.command()
	async def aesthetics(self, ctx, *convert):
		"""Converts text to be more  a e s t h e t i c s"""
		WIDE_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
		WIDE_MAP[0x20] = 0x3000
		convert = str(' '.join(convert)).translate(WIDE_MAP)
		return await ctx.send(convert)

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