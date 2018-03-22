import discord
import random
import re
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
		# sanitise input by removing all spaces, converting to lower case
		expression = expression.lower().replace(' ','')
		# check end of expression for a 'x<number>'
		parts = expression.split('x',1)
		times = 1
		if len(parts) == 2:
			try:
				times = int(parts[1])
				if times < 1:
					time = 1;
			except ValueError:
				times = 1##might want to add error report to user to say its not valid so they dont make the mistake again
		m=re.findall('(-?)((?:(\d*)d(\d*))|\d+)(r\d*)?([h,l]{1}\d*)?',parts[0])
		if m == []:
			return await ctx.send('Ase TBTerra to write proper useage')
		dice = []
		for item in m:
			temp = [0]*5
			temp[0] = 1 if item[0] == '' else -1
			if 'd' in item[1]:
				if item[2] == '':
					temp[1] = 1
					temp[2] = int(item[3])
				else:
					temp[1] = int(item[2])
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
		response = ''
		for i in range(times):
			total = 0
			if times > 1:
				response += 'Roll {}: '.format(i+1)
			else:
				response += 'Rolled: '
			for j in range(len(dice)):
				if j != 0:
					response += ' + '
				if dice[j][0] == -1:
					response += '-'
				if dice[j][2] == 1:
					response += '{}'.format(dice[j][1])
					total += dice[j][0] * dice[j][1]
				else:
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
						response += '{},'.format(temp[k][1])
						total+= dice[j][0] * temp[k][0]
					response = response[:-1] + ')'
			response += ' Totaling: {}'.format(total)
			if i < (times-1): response += '\n'
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
		if ctx.guild.id == 393764974444675073:
			await self.bot.get_channel(394959819796381697).send("{} used the aesthetics command passing the argument '{}'".format(str(ctx.author), ' '.join(convert)))
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