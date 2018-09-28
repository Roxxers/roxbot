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


import discord
from discord.ext import commands

import roxbot
from roxbot import guild_settings as gs

# TODO: Clean up this file.

def is_owner_or_admin():
	def predicate(ctx):
		if ctx.author.id == roxbot.owner:
			return True
		elif isinstance(ctx.channel, discord.DMChannel):
			return False
		else:
			for role in ctx.author.roles:
				if role.id in gs.get(ctx.guild).perm_roles["admin"]:
					return True
		return False
	return commands.check(predicate)


def _is_admin_or_mod(ctx):
	if ctx.message.author.id == roxbot.owner:
		return True
	elif isinstance(ctx.channel, discord.DMChannel):
		return False
	else:
		admin_roles = gs.get(ctx.guild).perm_roles["admin"]
		mod_roles = gs.get(ctx.guild).perm_roles["mod"]
		for role in ctx.author.roles:
			if role.id in mod_roles or role.id in admin_roles:
				return True
	return False


def is_admin_or_mod():
	return commands.check(_is_admin_or_mod)


def nsfw_predicate(ctx):
	if isinstance(ctx.channel, discord.DMChannel):
		return False
	nsfw = gs.get(ctx.guild).nsfw
	if not nsfw["channels"] and nsfw["enabled"]:
		return nsfw["enabled"] == 1
	elif nsfw["enabled"] and nsfw["channels"]:
		return ctx.channel.id in nsfw["channels"]
	else:
		return False


def is_nfsw_enabled():
	return commands.check(lambda ctx: nsfw_predicate(ctx))


def isnt_anal():
	def predicate(ctx):
		if isinstance(ctx.channel, discord.DMChannel):
			return False
		anal = gs.get(ctx.guild).is_anal["y/n"]
		if not anal or (nsfw_predicate(ctx) and gs.get(ctx.guild).is_anal["y/n"]):
			return True
		else:
			return False
	return commands.check(predicate)
