from discord import ActivityType
from discord.ext import commands

import roxbot


class Twitch():
	"""
	A cog that handles posting when users go live on Twitch
	"""
	def __init__(self, bot_client):
		self.bot = bot_client

	async def on_member_update(self, member_b, member_a):
		"""Twitch Shilling Part"""
		twitch = roxbot.guild_settings.get(member_b.guild).twitch
		if roxbot.blacklisted(member_b) or not twitch["enabled"]:
			return

		if member_a.activitiy:
			if member_a.activity.type == ActivityType.streaming and member_b.activity.type != ActivityType.streaming:
				if not twitch["whitelist"]["enabled"] or member_a.id in twitch["whitelist"]["list"]:
					channel = self.bot.get_channel(twitch["channel"])
					return await channel.send(":video_game:** {} is live!** :video_game:\n{}\n{}".format(
						member_a.name, member_a.game.name, member_a.game.url))

	@commands.group()
	@roxbot.checks.is_admin_or_mod()
	async def whitelist(self, ctx):
		"""Command group that handles the twitch cog's whitelist."""
		if ctx.invoked_subcommand is None:
			return await ctx.send('Missing Argument')

	@whitelist.command()
	async def enable(self, ctx):
		"""Enables the twitch shilling whitelist. Repeat the command to disable.
		Usage:
			;whitelist enable"""
		settings = roxbot.guild_settings.get(ctx.guild)
		if not settings.twitch["whitelist"]["enabled"]:
			settings.twitch["whitelist"]["enabled"] = 1
			settings.update(settings.twitch, "twitch")
			return await ctx.send("Whitelist for Twitch shilling has been enabled.")
		else:
			settings.twitch["whitelist"]["enabled"] = 0
			settings.update(settings.twitch, "twitch")
			return await ctx.send("Whitelist for Twitch shilling has been disabled.")

	@whitelist.command()
	async def edit(self, ctx, option, mentions=None):
		"""Adds or removes users to the whitelist. Exactly the same as the blacklist command in usage."""

		# TODO: This is all horribly outdated useage and needs to be rewritten.

		whitelist_count = 0
		settings = roxbot.guild_settings.get(ctx.guild)

		if not ctx.message.mentions and option != 'list':
			return await ctx.send("You haven't mentioned anyone to whitelist.")

		if option not in ['+', '-', 'add', 'remove', 'list']:
			return await ctx.send('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

		if option in ['+', 'add']:
			for user in ctx.message.mentions:
				settings.twitch["whitelist"]["list"].append(user.id)
				whitelist_count += 1
			settings.update(settings.twitch, "twitch")
			return await ctx.send('{} user(s) have been added to the whitelist'.format(whitelist_count))

		elif option in ['-', 'remove']:
			for user in ctx.message.mentions:
				if user.id in settings.twitch["whitelist"]["list"]:
					settings.twitch["whitelist"]["list"].remove(user.id)
					whitelist_count += 1
			settings.update(settings.twitch, "twitch")
			return await ctx.send('{} user(s) have been removed to the whitelist'.format(whitelist_count))

		elif option == 'list':
			return await ctx.send(settings.twitch["whitelist"]["list"])


def setup(bot_client):
	bot_client.add_cog(Twitch(bot_client))
