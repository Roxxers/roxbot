import os
import math
import roxbot
import discord
from PIL import Image
from discord.ext import commands


class PrideFlags:
	"""Class to produce pride flags for the filters in roxbot."""
	def __init__(self, rows=0, colours=None, even=True, ratio=None):
		self.rows = rows
		self.colours = colours
		self.even = even
		self.ratio = ratio or [(1/rows)]*rows  # Custom ratio is here for things like the bi pride flag

	@classmethod
	def lgbt(cls):
		rows = 6
		red = (243, 28, 28)
		orange = (255, 196, 0)
		yellow = (255, 247, 0)
		green = (0, 188, 108)
		blue = (0, 149, 255)
		violet = (181, 46, 193)
		colours = (red, orange, yellow, green, blue, violet)
		return cls(rows=rows, colours=colours)

	@classmethod
	def trans(cls):
		rows = 5
		blue = (91, 206, 250)
		pink = (245, 169, 184)
		white = (255, 255, 255)
		colours = (blue, pink, white, pink, blue)
		return cls(rows=rows, colours=colours)


class CustomCommands:
	def __init__(self, bot_client):
		self.bot = bot_client

	@staticmethod
	async def flag_filter(name, flag, user):
		"""At the moment, can only make horizontal stripe flags"""
		url = user.avatar_url_as(static_format="png")
		if url.split(".")[-1] == "gif":
			f = '{0.name}.gif'.format(user)
		else:
			f = '{0.name}.png'.format(user)

		await roxbot.http.download_file(url, f)

		ava = Image.open(f)

		top = 0
		bottom = int(math.ceil(
			ava.height * flag.ratio[0]))  # we use math.ceil here to avoid rounding errors when converting float to int

		for x, colour in enumerate(flag.colours):
			# Grab the next slice of the images height and width
			height = int(math.ceil(ava.height * flag.ratio[x]))
			width = ava.width
			box = (0, top, width, bottom)
			# Make the colour block and the transparency mask at the slice size. Then crop the next part of the image
			row = Image.new('RGB', (width, height), colour)
			mask = Image.new('RGBA', (width, height), (0, 0, 0, 123))
			slice = ava.crop(box)
			# Combine all three and paste it back into original image
			part = Image.composite(slice, row, mask)
			ava.paste(part, box)
			top += height
			bottom += height

		filename = name + f
		ava.save(filename)
		os.remove(f)
		file = discord.File(filename)
		return file

	@commands.group(case_insensitive=True)
	async def filter(self, ctx):
		pass

	@filter.command()
	async def lgbt(self, ctx, user: discord.Member=None):
		if not user:
			user = ctx.author

		flag = PrideFlags.lgbt()
		async with ctx.typing():
			file = await self.flag_filter("lgbt", flag, user)
		await ctx.send(file=file)
		os.remove(file.filename)

	@filter.command()
	async def trans(self, ctx, user:discord.Member=None):
		if not user:
			user = ctx.author

		flag = PrideFlags.trans()
		async with ctx.typing():
			file = await self.flag_filter("trans", flag, user)
		await ctx.send(file=file)
		os.remove(file.filename)


def setup(bot_client):
	bot_client.add_cog(CustomCommands(bot_client))
