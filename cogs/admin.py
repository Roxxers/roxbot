import datetime
import discord
from discord.ext.commands import bot

import checks

class Admin():
	"""
	Admin Commands for those admins
	"""
	def __init__(self, Bot):
		self.bot = Bot

	@checks.is_owner_or_admin()
	@bot.command(pass_context=True)
	async def emojiuse(self, ctx, emoji, *args):
		# TODO: Add check that emoji is an emoji
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
				else:
					pass
			return usage

		# Command

		await self.bot.say("Warning! This command may take upto 15 minutes to process. Please do no spam me. I am working.", delete_after=20)
		await self.bot.send_typing(ctx.message.channel)

		if all_emojis:
			emoji_usage = {}
			for emoji in ctx.message.server.emojis:
				emoji_usage[emoji.id] = await count_uses()

			em = discord.Embed(colour=0xDEADBF)
			for emoji in emoji_usage:
				emoji_obj = discord.utils.get(ctx.message.server.emojis, id=emoji)
				amount = sum(emoji_usage[emoji])
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



def setup(Bot):
	Bot.add_cog(Admin(Bot))
