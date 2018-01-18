import discord
import checks
from discord.ext.commands import bot, group

class Admin():
	"""
	Admin Commands for those admins
	"""
	def __init__(self, Bot):
		self.bot = Bot

	@checks.is_owner_or_admin()
	@bot.command(pass_context=True)
	async def emojiuse(self, ctx, emoji, *args):
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
					async for message in self.bot.logs_from(channel, limit=20000):
						if str(emoji) in message.content:
							x += 1
					usage[channel.id] = x
				else:
					pass
			return usage

		# Command

		await self.bot.say("Warning! This command may take upto 5 minutes to process. Please do no spam me. I am working.", delete_after=20)
		await self.bot.send_typing(ctx.message.channel)

		if all_emojis:
			emoji_usage = {}
			for emoji in ctx.message.server.emojis:
				emoji_usage[emoji.id] = await count_uses()

			em = discord.Embed()
			for emoji in emoji_usage:
				emoji_obj = discord.utils.get(ctx.message.server.emojis, id=emoji)
				em.add_field(name=str(emoji_obj), value=sum(emoji_usage[emoji]))
			return await self.bot.say(embed=em)

		else:
			usage = await count_uses()

			if verbose:
				amount = sum(usage)
				output = verbose_output(usage)
				output_em = discord.Embed(description = output)
				return await self.bot.say(content = "{} has been used {} time(s). Here is the break down per channel.".format(emoji, amount), embed=output_em)

			else: # Non-verbose output
				amount = sum(usage)
				return await self.bot.say("{} has been used {} time(s) server wide.".format(emoji, amount))



def setup(Bot):
	Bot.add_cog(Admin(Bot))
