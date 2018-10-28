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


import os
import math
import random
import numpy as np
from PIL import Image, ImageEnhance

import roxbot
import discord
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

	@classmethod
	def gf(cls):
		rows = 5
		pink = (255, 117, 162)
		white = (255, 255, 255)
		purple = (190, 24, 214)
		black = (0, 0, 0)
		blue = (51, 62, 189)
		colours = (pink, white, purple, black, blue)
		return cls(rows=rows, colours=colours)

	@classmethod
	def agender(cls):
		rows = 7
		black = (0, 0, 0)
		white = (255, 255, 255)
		grey = (185, 185, 185)
		green = (176, 244, 141)
		colours = (black, grey, white, green, white, grey, black)
		return cls(rows=rows, colours=colours)


class ImageEditor:
	def __init__(self, bot_client):
		self.bot = bot_client

	@staticmethod
	def image_lookup(message):
		try:
			if message.attachments[0].height:  # Check if attachment is image
				return message.attachments[0].url
		except IndexError:
			return message.author.avatar_url_as(format="png")

	@staticmethod
	def add_grain(img, prob=0.2, opacity=30):
		"""
		Adds salt and pepper grain to the given image.
		:param img: :type PIL.Image: Image to add grain to
		:param prob: :type float: Probability of a pixel being black between 0-1
		:param opacity: :type int: opacity of the grain when composite with the given image between 0%-100%
		:return: :type PIL.Image: Image with added grain
		"""
		img_matrix = np.zeros((img.height, img.width), dtype=np.uint8)
		for y in range(img.height):
			for x in range(img.width):
				if prob < random.random():
					img_matrix[y][x] = 255
		noisy = Image.fromarray(img_matrix, "L")
		noisy = noisy.convert("RGB")
		mask = Image.new('RGBA', img.size, (0, 0, 0, opacity))
		return Image.composite(noisy, img, mask)

	@staticmethod
	async def flag_filter(name, flag, url):
		"""At the moment, can only make horizontal stripe flags"""

		f = 'filter_{}.png'.format(name)

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

		os.remove(f)
		ava.save(f)
		file = discord.File(f)
		return file

	async def image_logging(self, ctx, output):
		"""Logging function for all image commands to avoid shit loads or repeating code.
		Required because image has outputs that are user decided and therefore could need logging for."""
		logging = roxbot.guild_settings.get(ctx.guild)["logging"]
		log_channel = self.bot.get_channel(logging["channel"])
		return await roxbot.log(
			ctx.guild,
			log_channel,
			"image",
			User=ctx.author,
			User_ID=ctx.author.id,
			Output_Message_ID=output.id,
			Channel=ctx.channel,
			Channel_Mention=ctx.channel.mention,
			Time="{:%a %Y/%m/%d %H:%M:%S} UTC".format(ctx.message.created_at)
		)

	@commands.group(case_insensitive=True)
	async def pride(self, ctx):
		"""A collection of filters that show simple LGBT pride flags over the image provided.
		The filters work with either your pfp, someone elses', or an image provided either by attachment or URL."""
		if ctx.invoked_subcommand is None:
			raise commands.CommandNotFound(ctx.subcommand_passed)

	@pride.command()
	async def lgbt(self, ctx, image: roxbot.converters.AvatarURL=None):
		"""Adds a LGBT Pride Flag filter to the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)

		flag = PrideFlags.lgbt()
		async with ctx.typing():
			file = await self.flag_filter("lgbt", flag, image)
		output = await ctx.send(file=file)
		os.remove(file.filename)
		await self.image_logging(ctx, output)


	@pride.command(aliases=["trans"])
	async def transgender(self, ctx, image: roxbot.converters.AvatarURL=None):
		"""Adds a Trans Pride Flag filter to the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)

		flag = PrideFlags.trans()
		async with ctx.typing():
			file = await self.flag_filter("trans", flag, image)
		output = await ctx.send(file=file)
		os.remove(file.filename)
		await self.image_logging(ctx, output)

	@pride.command(aliases=["nb", "enby"])
	async def nonbinary(self, ctx, image: roxbot.converters.AvatarURL=None):
		"""Adds a Non-Binary Pride Flag filter to the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)

		flag = PrideFlags.non_binary()
		async with ctx.typing():
			file = await self.flag_filter("nb", flag, image)
		output = await ctx.send(file=file)
		os.remove(file.filename)
		await self.image_logging(ctx, output)

	@pride.command(aliases=["bi"])
	async def bisexual(self, ctx, image: roxbot.converters.AvatarURL=None):
		"""Adds a Bisexual Pride Flag filter to the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)

		flag = PrideFlags.bi()
		async with ctx.typing():
			file = await self.flag_filter("bi", flag, image)
		output = await ctx.send(file=file)
		os.remove(file.filename)
		await self.image_logging(ctx, output)

	@pride.command(aliases=["gq"])
	async def genderqueer(self, ctx, image: roxbot.converters.AvatarURL=None):
		"""Adds a Gender Queer Pride Flag filter to the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)

		flag = PrideFlags.gq()
		async with ctx.typing():
			file = await self.flag_filter("gq", flag, image)
		output = await ctx.send(file=file)
		os.remove(file.filename)
		await self.image_logging(ctx, output)

	@pride.command(aliases=["pan"])
	async def pansexual(self, ctx, image: roxbot.converters.AvatarURL=None):
		"""Adds a Pansexual Pride Flag filter to the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)

		flag = PrideFlags.pan()
		async with ctx.typing():
			file = await self.flag_filter("pan", flag, image)
		output = await ctx.send(file=file)
		os.remove(file.filename)
		await self.image_logging(ctx, output)

	@pride.command(aliases=["ace"])
	async def asexual(self, ctx, image: roxbot.converters.AvatarURL=None):
		"""Adds an Asexual Pride Flag filter to the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)

		flag = PrideFlags.ace()
		async with ctx.typing():
			file = await self.flag_filter("ace", flag, image)
		output = await ctx.send(file=file)
		os.remove(file.filename)
		await self.image_logging(ctx, output)

	@pride.command(aliases=["gf"])
	async def genderfluid(self, ctx, image: roxbot.converters.AvatarURL = None):
		"""Adds a Gender Fluid Pride Flag filter to the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)

		flag = PrideFlags.gf()
		async with ctx.typing():
			file = await self.flag_filter("gf", flag, image)
		output = await ctx.send(file=file)
		os.remove(file.filename)
		await self.image_logging(ctx, output)

	@pride.command()
	async def agender(self, ctx, image: roxbot.converters.AvatarURL = None):
		"""Adds an Agender Pride Flag filter to the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)

		flag = PrideFlags.agender()
		async with ctx.typing():
			file = await self.flag_filter("agender", flag, image)
		output = await ctx.send(file=file)
		os.remove(file.filename)
		await self.image_logging(ctx, output)

	@commands.command(aliases=["df"])
	async def deepfry(self, ctx, image: roxbot.converters.AvatarURL=None):
		"""Deepfrys the given image
		Args:
			image: Optional
				If nothing, your avatar
				Mention a user, their avatar
				Provide a URL, that image
				Provide an image via upload, that image.
		"""
		if not image:
			image = self.image_lookup(ctx.message)
		filename = await roxbot.http.download_file(image)

		async with ctx.typing():
			# Convert to jpg
			if filename.split(".")[-1] != "jpg":
				jpg_name = filename.split(".")[0] + ".jpg"
				img = Image.open(filename)
				img = img.convert(mode="RGB")
				img.save(jpg_name)
				os.remove(filename)
			else:
				jpg_name = filename

			img = Image.open(jpg_name)

			# Brightness Enhance

			ehn = ImageEnhance.Brightness(img)
			img = ehn.enhance(1.25)

			# Contrast Enhance
			ehn = ImageEnhance.Contrast(img)
			img = ehn.enhance(1.5)

			# Sharpness Enhance
			ehn = ImageEnhance.Sharpness(img)
			img = ehn.enhance(20)

			# Saturation Enhance
			ehn = ImageEnhance.Color(img)
			img = ehn.enhance(2)

			# Add Salt and Pepper Noise

			img = self.add_grain(img)

			img.save(jpg_name)

			# JPG-fy image
			for x in range(20):
				img = Image.open(jpg_name)
				img = img.convert(mode="RGB")
				img.save(jpg_name)

			output = await ctx.send(file=discord.File(jpg_name))
		os.remove(jpg_name)
		await self.image_logging(ctx, output)


def setup(bot_client):
	bot_client.add_cog(ImageEditor(bot_client))
