from asyncio import TimeoutError


async def delete_option(bot, ctx, message, delete_emoji, timeout=20):
	"""Utility function that allows for you to add a delete option to the end of a command.
	This makes it easier for users to control the output of commands, esp handy for random output ones."""
	await message.add_reaction(delete_emoji)

	def check(r, u):
		print(r.emoji)
		return str(r) == str(delete_emoji) and u == ctx.author

	try:
		await bot.wait_for("reaction_add", timeout=timeout, check=check)
		await message.delete()
		return await ctx.send("{} requested output be deleted.".format(ctx.author))
	except TimeoutError:
		await message.remove_reaction(delete_emoji, bot.user)


def blacklisted(user):
	with open("roxbot/settings/blacklist.txt", "r") as fp:
		for line in fp.readlines():
			if str(user.id)+"\n" == line:
				return True
	return False
