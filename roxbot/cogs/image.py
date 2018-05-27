import os
import math
import roxbot
import discord
from PIL import Image
from discord.ext import commands


class PrideFlags:
	"""Class to produce pride flags for the filters in Roxbot."""
	def __init__(self, rows=0, colours=None, ratio=None):
		self.rows = rows
		self.colours = colours
		self.ratio = ratio or tuple([(1/rows)]*rows)  # Custom ratio is here for things like the bi pride flag

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

	@classmethod
	def non_binary(cls):
		rows = 4
		yellow = (255, 244, 51)
		white = (255, 255, 255)
		purple = (155, 89, 208)
		grey = (45, 45, 45)
		colours = (yellow, white, purple, grey)
		return cls(rows=rows, colours=colours)

	@classmethod
	def bi(cls):
		rows = 3
		ratio = (0.4, 0.2, 0.4)
		pink = (215, 2, 112)
		lavender = (115, 79, 150)
		blue = (0, 56, 168)
		colours = (pink, lavender, blue)
		return cls(rows=rows, colours=colours, ratio=ratio)

	@classmethod
	def pan(cls):
		rows = 3
		pink = (255, 33, 140)
		yellow = (255, 216, 0)
		blue = (33, 177, 255)
		colours = (pink, yellow, blue)
		return cls(rows=rows, colours=colours)

	@classmethod
	def ace(cls):
		rows = 4
		black = (0, 0, 0)
		grey = (163, 163, 163)
		white = (255, 255, 255)
		purple = (128, 0, 128)
		colours = (black, grey, white, purple)
		return cls(rows=rows, colours=colours)

	@classmethod
	def gq(cls):
		rows = 3
		purple = (181, 126, 220)
		white = (255, 255, 255)
		green = (74, 129, 35)
		colours = (purple, white, green)
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
		top = 0  # In the box we use, top is used to define which part of the image we are working on
		bottom = 0  # And bottom defines the height. That should help you visualise why I increment the values the way I do

		for x, colour in enumerate(flag.colours):
			# Grab the next slice of the images height and width
			# we use math.ceil here to avoid rounding errors when converting float to int
			height = int(math.ceil(ava.height * flag.ratio[x]))
			width = ava.width
			bottom += height
			box = (0, top, width, bottom)

			# Make the colour block and the transparency mask at the slice size. Then crop the next part of the image
			row = Image.new('RGB', (width, height), colour)
			mask = Image.new('RGBA', (width, height), (0, 0, 0, 123))
			crop = ava.crop(box)

			# Combine all three and paste it back into original image
			part = Image.composite(crop, row, mask)
			ava.paste(part, box)

			top += height

		filename = name + f
		ava.save(filename)
		os.remove(f)
		file = discord.File(filename)
		return file

	@commands.group(case_insensitive=True)
	async def pride(self, ctx):
		"""A collection of filters that show simple LGBT pride flags over the image provided."""
		pass

	@pride.command()
	async def lgbt(self, ctx, user: discord.Member=None):
		if not user:
			user = ctx.author

		flag = PrideFlags.lgbt()
		async with ctx.typing():
			file = await self.flag_filter("lgbt", flag, user)
		await ctx.send(file=file)
		os.remove(file.filename)

	@pride.command(aliases=["transgender"])
	async def trans(self, ctx, user: discord.Member=None):
		if not user:
			user = ctx.author

		flag = PrideFlags.trans()
		async with ctx.typing():
			file = await self.flag_filter("trans", flag, user)
		await ctx.send(file=file)
		os.remove(file.filename)

	@pride.command(aliases=["nonbinary", "nb"])
	async def enby(self, ctx, user: discord.Member=None):
		if not user:
			user = ctx.author

		flag = PrideFlags.non_binary()
		async with ctx.typing():
			file = await self.flag_filter("nb", flag, user)
		await ctx.send(file=file)
		os.remove(file.filename)

	@pride.command(aliases=["bisexual"])
	async def bi(self, ctx, user: discord.Member=None):
		if not user:
			user = ctx.author

		flag = PrideFlags.bi()
		async with ctx.typing():
			file = await self.flag_filter("bi", flag, user)
		await ctx.send(file=file)
		os.remove(file.filename)

	@pride.command(aliases=["genderqueer"])
	async def gq(self, ctx, user: discord.Member=None):
		if not user:
			user = ctx.author

		flag = PrideFlags.gq()
		async with ctx.typing():
			file = await self.flag_filter("gq", flag, user)
		await ctx.send(file=file)
		os.remove(file.filename)

	@pride.command(aliases=["pansexual"])
	async def pan(self, ctx, user: discord.Member=None):
		if not user:
			user = ctx.author

		flag = PrideFlags.pan()
		async with ctx.typing():
			file = await self.flag_filter("pan", flag, user)
		await ctx.send(file=file)
		os.remove(file.filename)

	@pride.command(aliases=["asexual"])
	async def ace(self, ctx, user: discord.Member=None):
		if not user:
			user = ctx.author

		flag = PrideFlags.ace()
		async with ctx.typing():
			file = await self.flag_filter("pan", flag, user)
		await ctx.send(file=file)
		os.remove(file.filename)


def setup(bot_client):
	bot_client.add_cog(CustomCommands(bot_client))
