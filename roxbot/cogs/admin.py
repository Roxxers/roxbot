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


import time
import discord
import datetime
from discord.ext import commands

import roxbot
from roxbot import guild_settings as gs


def _is_admin_or_mod(message):
	if message.author.id == roxbot.owner:
		return True
	perm_roles = gs.get(message.channel.guild).perm_roles
	for role in message.author.roles:
		if role.id in perm_roles.get("admin") or role.id in perm_roles.get("mod"):
			return True
	return False


class Admin:
	"""
	Admin Commands for those admins
	"""

	OK_SLOWMODE_ON = "Slowmode on :snail: ({} seconds)"
	OK_SLOWMODE_OFF = "Slowmode off"
	OK_SLOWMODE_CHANGED = "Slowmode set to :snail: ({} seconds)"
	ERROR_SLOWMODE_SECONDS = "Rate limit has to be between 0-120."

	OK_PURGE_CONFIRMATION = "{} message(s) purged from chat."

	OK_WARN_ADD = "Reported {}."
	OK_WARN_ADD_USER_LIMIT_DM = "{} has been reported {} time(s). This is a reminder that this is over the set limit of {}."
	WARN_WARN_ADD_LIMIT_REACHED = "You can only warn a user {} times!"

	OK_WARN_LIST_NO_WARNINGS = "No warnings on record."
	OK_WARN_LIST_USER_NO_WARNINGS = "This user doesn't have any warning on record."

	OK_WARN_REMOVE_REMOVED_WARNING = "Removed Warning {} from {}"
	OK_WARN_REMOVE_REMOVED_WARNINGS = "Removed all warnings for {}"
	WARN_WARN_REMOVE_USER_NOT_FOUND = "Could not find user {} in warning list."
	ERROR_WARN_REMOVE_INDEXERROR = "Index Error: Warning index doesn't exist. User only has {} warning(s)."
	ERROR_WARN_REMOVE_VALUEERROR = "Value Error: Please enter a valid index number."

	OK_WARN_PRUNE_PRUNED = "Pruned {} banned users from the warn list."

	OK_WARN_SL_SET = "Number of warnings needed to DM's set to {}"
	OK_WARN_SL_SET_ZERO = "DM's to mods for warning limits disabled."
	ERROR_WARN_SL_NEG = "number_of_warnings can only be a positive integer."

	OK_MOD_ACTION = "{} with reason: '{}'"
	WARN_MOD_LACK_PERMS = "Cannot kick owner or users higher or equal to me role hierarchy."
	WARN_UNBAN_NOTFOUND = "User is not banned."

	def __init__(self, bot_client):
		self.bot = bot_client
		self.settings = {
			"admin": {
				"convert": {"warnings": "hide"},
				"admin_roles": [],
				"mod_roles": [],
				"is_anal": 0,
				"warning_limit": 0,
				"warnings": {},
			}
		}

	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.command()
	async def slowmode(self, ctx, seconds: int):
		"""Puts the current channel in slowmode. Requires the Manage Messages permission.
		Users with manage_channel or manage_messages permissions will not be effected.
		Usage:
			;slowmode [time]
			seconds =  number of seconds for the cooldown between messages a user has.
			0 turns off slowmode for this channel"""
		if seconds == 0:  # Turn Slow Mode off
			await ctx.channel.edit(slowmode_delay=seconds, reason="{} requested to turn off slowmode.".format(ctx.author))
			embed = discord.Embed(description=self.OK_SLOWMODE_OFF, colour=roxbot.EmbedColours.pink)
			return await ctx.send(embed=embed)

		elif 0 < seconds <= 120 and ctx.channel.slowmode_delay == 0:  # Turn Slow Mode On
			await ctx.channel.edit(slowmode_delay=seconds, reason="{} requested slowmode with a timer of {}".format(ctx.author, seconds))
			embed = discord.Embed(description=self.OK_SLOWMODE_ON.format(seconds), colour=roxbot.EmbedColours.pink)
			return await ctx.send(embed=embed)

		elif 0 < seconds <= 120 and ctx.channel.slowmode_delay > 0:  # Change value of Slow Mode timer
			await ctx.channel.edit(slowmode_delay=seconds, reason="{} requested slowmode timer be changed to {}".format(ctx.author, seconds))
			embed = discord.Embed(description=self.OK_SLOWMODE_CHANGED.format(seconds), colour=roxbot.EmbedColours.pink)
			return await ctx.send(embed=embed)
		elif seconds < 0 or seconds > 120:
			raise commands.BadArgument(self.ERROR_SLOWMODE_SECONDS)

	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True, read_message_history=True)
	@commands.cooldown(1, 5)
	@commands.command()
	async def purge(self, ctx, limit=0, *, author: roxbot.converters.User=None):
		"""Purges messages from the text channel. Requires the Manage Messages permission.
		Limit = Limit of messages to be deleted
		Author (optional) =  If given, roxbot will selectively only delete this user's messages."""
		# TODO: To sort out the limit == how many to delete for the author, and not just a limit.
		if author:
			predicate = lambda message: message.author.id == author.id and message.id != ctx.message.id
		else:
			predicate = lambda message: message.id != ctx.message.id
		messages = await ctx.channel.purge(limit=limit, check=predicate)
		embed = discord.Embed(description=self.OK_PURGE_CONFIRMATION.format(len(messages)), colour=roxbot.EmbedColours.pink)
		return await ctx.send(embed=embed)

	@commands.guild_only()
	@commands.has_permissions(kick_members=True)
	@commands.group(case_insensitive=True)
	async def warn(self, ctx):
		"""Group of commands handling . Requires the Kick Members permission."""
		if ctx.invoked_subcommand is None:
			raise commands.CommandNotFound(ctx.subcommand_passed)

	@warn.command()
	async def add(self, ctx, user: discord.User=None, *, warning=""):
		"""Adds a warning to a user."""
		# Warning in the settings is a dictionary of user ids. The user ids are equal to a list of dictionaries.
		settings = gs.get(ctx.guild)
		warnings = settings["admin"]["warnings"]
		warning_limit = settings["admin"]["warning_limit"]
		warning_dict = {
			"warned-by": ctx.author.id,
			"date": time.time(),
			"warning": warning
		}
		user_id = str(user.id)

		if user_id not in warnings:
			warnings[user_id] = []

		warn_limit = 10
		if len(warnings[user_id]) > warn_limit:
			embed = discord.Embed(description=self.WARN_WARN_ADD_LIMIT_REACHED.format(warn_limit), colour=roxbot.EmbedColours.red)
			return await ctx.send()

		warnings[user_id].append(warning_dict)
		settings["admin"]["warnings"] = warnings
		settings.update(settings["admin"], "admin")

		amount_warnings = len(warnings[user_id])
		if amount_warnings >= warning_limit > 0:
			await ctx.author.send(self.OK_WARN_ADD_USER_LIMIT_DM.format(str(user), amount_warnings, warning_limit))

		embed = discord.Embed(description=self.OK_WARN_ADD.format(str(user)), colour=roxbot.EmbedColours.pink)
		return await ctx.send(embed=embed)

	@warn.command()
	async def list(self, ctx, *, user: roxbot.converters.User=None):
		"""Lists all or just the warnings for one user."""
		settings = gs.get(ctx.guild)
		warnings = settings["admin"]["warnings"]

		if user is None:
			paginator = commands.Paginator()
			for member in warnings:
				# Remove users with no warning here instead of remove cause im lazy
				if not warnings[member]:
					warnings.pop(member)
				else:
					member_obj = discord.utils.get(ctx.guild.members, id=int(member))
					if member_obj:
						paginator.add_line("{}: {} Warning(s)".format(str(member_obj), len(warnings[member])))
					else:
						paginator.add_line("{}: {} Warning(s)".format(member, len(warnings[member])))
			# This is in case we have removed some users from the list.
			settings["admin"]["warnings"] = warnings
			settings.update(settings["admin"], "admin")

			if len(paginator.pages) <= 0:
				embed = discord.Embed(description=self.OK_WARN_LIST_NO_WARNINGS, colour=roxbot.EmbedColours.orange)
				return await ctx.send(embed=embed)
			for page in paginator.pages:
				await ctx.send(embed=discord.Embed(description=page, colour=roxbot.EmbedColours.pink))
		else:
			user_id = str(user.id)

			if not warnings.get(user_id):
				embed = discord.Embed(description=self.OK_WARN_LIST_USER_NO_WARNINGS, colour=roxbot.EmbedColours.orange)
				return await ctx.send(embed=embed)

			em = discord.Embed(title="Warnings for {}".format(str(user)), colour=roxbot.EmbedColours.pink)
			em.set_thumbnail(url=user.avatar_url)

			x = 1
			userlist = warnings[user_id]
			for warning in userlist:
				try:
					warned_by = str(await self.bot.get_user_info(warning["warned-by"]))
				except discord.ext.commands.CommandInvokeError:
					warned_by = warning["warned-by"]
				date = roxbot.datetime_formatting.format(datetime.datetime.fromtimestamp(warning["date"]))
				warn_reason = warning["warning"]
				em.add_field(name="Warning %s" % x, value="Warned by: {}\nTime: {}\nReason: {}".format(warned_by, date, warn_reason))
				x += 1
			return await ctx.send(embed=em)

	@warn.command()
	async def remove(self, ctx, user: roxbot.converters.User=None, index=None):
		"""Removes one or all of the warnings for a user."""
		user_id = str(user.id)
		settings = gs.get(ctx.guild)
		warnings = settings["admin"]["warnings"]

		if index:
			try:
				index = int(index)
				index -= 1
				warnings[user_id].pop(index)
				if not warnings[user_id]:
					warnings.pop(user_id)

				settings["admin"]["warnings"] = warnings
				settings.update(settings["admin"], "admin")
				embed = discord.Embed(description=self.OK_WARN_REMOVE_REMOVED_WARNING.format(index+1, str(user)), colour=roxbot.EmbedColours.pink)
				return await ctx.send(embed=embed)

			except Exception as e:
				embed = discord.Embed(colour=roxbot.EmbedColours.red)
				if isinstance(e, IndexError):
					embed.description = self.ERROR_WARN_REMOVE_INDEXERROR.format(len(settings["warnings"][user_id]))
				elif isinstance(e, KeyError):
					embed.description = self.WARN_WARN_REMOVE_USER_NOT_FOUND.format(str(user))
				elif isinstance(e, ValueError):
					embed.description = self.ERROR_WARN_REMOVE_VALUEERROR
				else:
					raise e
				return ctx.send(embed=embed)
		else:
			try:
				warnings.pop(user_id)
				settings["admin"]["warnings"] = warnings
				settings.update(settings["admin"], "admin")
				embed = discord.Embed(description=self.OK_WARN_REMOVE_REMOVED_WARNINGS.format(str(user)), colour=roxbot.EmbedColours.pink)
				return await ctx.send(embed=embed)
			except KeyError:
				embed = discord.Embed(description=self.WARN_WARN_REMOVE_USER_NOT_FOUND.format(str(user)), colour=roxbot.EmbedColours.orange)
				return await ctx.send(embed=embed)

	@commands.bot_has_permissions(ban_members=True)
	@warn.command()
	async def prune(self, ctx, dry_run=0):
		"""Purges banned users from the warn list. Add a 1 at the end to do a dry run."""
		settings = gs.get(ctx.guild)
		warnings = settings["admin"]["warnings"].copy()
		count = 0
		for ban in await ctx.guild.bans():
			for user in warnings:
				if int(user) == ban.user.id:
					if dry_run == 0:
						settings["admin"]["warnings"].pop(user)
					count += 1
		settings.update(settings["admin"], "admin")
		embed = discord.Embed(description=self.OK_WARN_PRUNE_PRUNED.format(count), colour=roxbot.EmbedColours.pink)
		return await ctx.send(embed=embed)

	@warn.command(aliases=["set_limits", "sl", "setlimit", "setlimits"])
	async def set_limit(self, ctx, number_of_warnings: int):
		"""
		Sets the limit for how many warnings a user can get before mod's are notified.
		Example: if 3 is set, on the third warning, mods will be DM'd. If this is set to 0, DM's will be disabled.
		:param ctx:
		:param number_of_warnings: A positive integer.
		:return:
		"""
		if number_of_warnings < 0:
			raise commands.BadArgument(self.ERROR_WARN_SL_NEG)
		settings = gs.get(ctx.guild)
		admin = settings["admin"]
		admin["warning_limit"] = number_of_warnings
		settings.update(admin, "admin")
		if number_of_warnings == 0:
			embed = discord.Embed(description=self.OK_WARN_SL_SET_ZERO, colour=roxbot.EmbedColours.pink)
			return await ctx.send(embed=embed)
		else:
			embed = discord.Embed(description=self.OK_WARN_SL_SET.format(number_of_warnings), colour=roxbot.EmbedColours.pink)
			return await ctx.send(embed=embed)

	@commands.guild_only()
	@commands.has_permissions(kick_members=True)
	@commands.bot_has_permissions(kick_members=True)
	@commands.command()
	async def kick(self, ctx, member: discord.Member, *, reason=""):
		"""Kicks mentioned user. Allows you to give a reason. Requires the Kick Members permission."""
		try:
			await member.kick(reason=reason)
			embed = discord.Embed(description=self.OK_MOD_ACTION.format("Kicked", member, reason), colour=roxbot.EmbedColours.pink)
			return await ctx.send(embed=embed)
		except discord.Forbidden:
			embed = discord.Embed(description=self.WARN_MOD_LACK_PERMS, colour=roxbot.EmbedColours.red)
			return await ctx.send(embed=embed)

	@commands.guild_only()
	@commands.has_permissions(ban_members=True)
	@commands.bot_has_permissions(ban_members=True)
	@commands.command()
	async def ban(self, ctx, member: discord.Member, *, reason=""):
		"""Bans mentioned user. Allows you to give a reason. Requires the Ban Members permission."""
		try:
			await member.ban(reason=reason, delete_message_days=0)
			embed = discord.Embed(description=self.OK_MOD_ACTION.format("Banned", member, reason), colour=roxbot.EmbedColours.pink)
			return await ctx.send(embed=embed)
		except discord.Forbidden:
			embed = discord.Embed(description=self.WARN_MOD_LACK_PERMS, colour=roxbot.EmbedColours.red)
			return await ctx.send(embed=embed)

	@commands.guild_only()
	@commands.has_permissions(ban_members=True)
	@commands.bot_has_permissions(ban_members=True)
	@commands.command()
	async def unban(self, ctx, member: roxbot.converters.User, *, reason=""):
		"""Unbans user with given ID. Allows you to give a reason. Requires the Ban Members permission."""
		ban = await ctx.guild.get_ban(member)
		mem = ban.user
		if mem is None:
			embed = discord.Embed(description=self.WARN_UNBAN_NOTFOUND, colour=roxbot.EmbedColours.red)
			return await ctx.send(embed=embed)
		try:
			await ctx.guild.unban(mem, reason=reason)
			embed = discord.Embed(description=self.OK_MOD_ACTION.format("Unbanned", mem, reason), colour=roxbot.EmbedColours.pink)
			return await ctx.send(embed=embed)
		except discord.Forbidden:
			embed = discord.Embed(description=self.WARN_MOD_LACK_PERMS, colour=roxbot.EmbedColours.red)
			return await ctx.send(embed=embed)


def setup(bot_client):
	bot_client.add_cog(Admin(bot_client))
