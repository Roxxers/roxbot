# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017-2018 Roxanne Gibson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import asyncio


async def delete_option(bot, ctx, message, delete_emoji, timeout=20):
	"""Utility function that allows for you to add a delete option to the end of a command.
	This makes it easier for users to control the output of commands, esp handy for random output ones.

	Params
	=======
	bot: discord.ext.commands.Bot
		The current bot client
	ctx: discord.ext.commands.Context
		The context of the command
	message: discord.Message
		Output message from Roxbot
	delete_emoji: discord.Emoji or str if unicode emoji
		Used as the reaction for the user to click on.
	timeout: int (Optional)
		Amount of time in seconds for the bot to wait for the reaction. Deletes itself after the timer runes out.
		Set to 20 by default
	"""
	await message.add_reaction(delete_emoji)

	def check(r, u):
		return str(r) == str(delete_emoji) and u == ctx.author and r.message.id == message.id

	try:
		await bot.wait_for("reaction_add", timeout=timeout, check=check)
		await message.remove_reaction(delete_emoji, bot.user)
		await message.remove_reaction(delete_emoji, ctx.author)
		await message.edit(content="{} requested output be deleted.".format(ctx.author), embed=None)
	except asyncio.TimeoutError:
		await message.remove_reaction(delete_emoji, bot.user)


def blacklisted(user):
	"""Checks if given user is blacklisted from the bot.
	Params
	=======
	user: discord.User

	Returns
	=======
	If the user is blacklisted: bool"""
	with open("roxbot/settings/blacklist.txt", "r") as fp:
		for line in fp.readlines():
			if str(user.id)+"\n" == line:
				return True
	return False
