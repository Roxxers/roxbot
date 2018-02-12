import datetime
import checks
import discord
from discord.ext.commands import bot


class Admin():
	"""
	Admin Commands for those admins
	"""
	def __init__(self, Bot):
		self.bot = Bot
		self.slow_mode = False
		self.slow_mode_channels = {}
		self.users = {}

	async def on_message(self, message):
		# Slow Mode Code
		channel = message.channel
		author = message.author

		if not author == self.bot.user:
			if self.slow_mode and channel.id in self.slow_mode_channels:
				if author.id not in self.users[channel.id]:
					# If user hasn't sent a message in this channel after slow mode was turned on
					self.users[channel.id][author.id] = message.timestamp
				else:
					# Else, check when their last message was and if time is smaller than the timer, delete the message.
					timer = datetime.timedelta(seconds=self.slow_mode_channels[channel.id])
					if message.timestamp - self.users[channel.id][author.id] < timer:
						await self.bot.delete_message(message)
					else:
						self.users[message.channel.id][author.id] = message.timestamp
			else:
				pass

	@checks.not_pm()
	@checks.is_admin_or_mod()
	@bot.command(pass_context=True)
	async def slowmode(self, ctx, time):
		if time == "off" and self.slow_mode: # Turn Slow Mode off
			self.slow_mode = False
			self.slow_mode_channels.pop(ctx.message.channel.id)
			self.users.pop(ctx.message.channel.id)
			return await self.bot.say("Slowmode off")

		elif time.isdigit() and not self.slow_mode: # Turn Slow Mode On
			self.users[ctx.message.channel.id] = {}
			self.slow_mode_channels[ctx.message.channel.id] = int(time)
			self.slow_mode = True
			return await self.bot.say("Slowmode on :snail: ({} seconds)".format(time))

		elif time.isdigit and self.slow_mode: # Change value of Slow Mode timer
			self.slow_mode_channels[ctx.message.channel.id] = int(time)
			return await self.bot.say("Slowmode set to :snail: ({} seconds)".format(time))

		else:
			pass


	@checks.is_admin_or_mod()
	@bot.command(pass_context=True)
	async def emojiuse(self, ctx, emoji, *args):
		# TODO: Add check that emoji is an emoji
		# TODO: Disable so like when we go to 1.3 this isn't live cause it needs more work and it needs to be completed already
		# The way forward is clearly put the given emoji in and treat it as a list of emojis,
		# if all emojis, then generate the list. Allows for more than one emoji to be analysed. Works better for larger servers/

		# Flag Parsing

		if "-v" in args:
			verbose = True
		else:
			verbose = False
		if "-w" in args or emoji == "-w": # Second check just in case user just puts ";emojiuse -w"
			all_emojis = True
		else:
			all_emojis = False

		# Functions

		def sum(usage):
			amount = 0
			for channel in usage.values():
				amount += channel
			return amount

		def use_by_day(amount):
			useperday = amount / 30
			useperday = "{0:.2f}".format(useperday)
			return useperday


		def verbose_output(usage):
			output = ""
			for channel in usage:
				channel = self.bot.get_channel(channel)  # Convert channel from ID to channel object to get name
				output = output + "{}: {} \n".format(channel.name, usage[channel.id])
			return output

		async def count_uses():
			usage = {}
			for channel in  ctx.message.server.channels:
				if channel.type == discord.ChannelType.text: # Only looks at server's text channels
					x = 0
					async for message in self.bot.logs_from(channel, limit=1000000, after=datetime.datetime.now() + datetime.timedelta(-30)):
						if str(emoji) in message.content:
							x += 1
					usage[channel.id] = x
					print(str(emoji) + "HAS {} AMOUNT OF USES IN {}".format(x, str(channel)))

				else:
					pass
			print("EMOJI WAS USED {} TOTAL TIMES".format(sum(usage)))
			return usage

		async def count_all_emoji():
			whitelist = [":yeetpride:",":yeet:", ":transgendercat:", ":thonkspin:", ":thonkegg:", ":ThinkPride:", ":thinkinggaysounds:", ":thatsgoodnews", ":pansexualcat:", ":nonbinarycat: ", ":kappa:", ":icantputpunctuationinemojinames:", ":hellothere:", ":agendercat:", ":Hedgeok:", ":extremethink:", ":donttryit:", ":cutie:", ":catappa:", ":boots:", ":awoo:", ":anotherhappylanding:", ":angrygay:"]
			usage = {}

			for emote in ctx.message.server.emojis:
				name = ":{}:".format(emote.name)
				if name in whitelist:
					usage[emote.id] = 0

			for channel in  ctx.message.server.channels: # TODO: ADD COUNTING BY CHANNEL
				if channel.type == discord.ChannelType.text: # Only looks at server's text channels
					async for message in self.bot.logs_from(channel, limit=1000000, after=datetime.datetime.now() + datetime.timedelta(-30)):
						for emote in ctx.message.server.emojis:
							if str(emote) in message.content and ":{}:".format(emote.name) in whitelist:
								usage[emote.id] += 1
								print("{} found in message {}".format(str(emote), message.id))

			return usage

		# Command

		await self.bot.say("Warning! This command may take upto 15 minutes to process. Please do no spam me. I am working.", delete_after=20)
		await self.bot.send_typing(ctx.message.channel)

		if all_emojis:
			emoji_usage = await count_all_emoji()


			em = discord.Embed(colour=0xDEADBF)
			for emoji in emoji_usage:
				emoji_obj = discord.utils.get(ctx.message.server.emojis, id=emoji)
				amount = emoji_usage[emoji]
				useperday = use_by_day(amount)
				em.add_field(name=str(emoji_obj), value="Amount Used: {}\nUse/Day: {}".format(amount, useperday), inline=False)
			return await self.bot.say(content="Below is a report of all custom emoji on this server and how many times they have been used in the previous 30 days. This includes a usage/day ratio.", embed=em)

		else:
			usage = await count_uses()
			amount = sum(usage)
			useperday = use_by_day(amount)
			if verbose:
				output = verbose_output(usage)
				output_em = discord.Embed(description=output, colour=0xDEADBF)
				return await self.bot.say(content="{} has been used {} time(s) in the last month. That's {}/day. Here is the break down per channel.".format(emoji, amount, useperday), embed=output_em)

			else: # Non-verbose output
				return await self.bot.say("{} has been used {} time(s) in the last month. That's {}/day.".format(emoji, amount, useperday))


	@checks.is_admin_or_mod()
	@bot.command(pass_context=True)
	async def warn(self, ctx, user: discord.User = None):
		pass


def setup(Bot):
	Bot.add_cog(Admin(Bot))
