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


import roxbot

import discord
from discord.ext import commands


def has_permission_or_owner(**perms):
	def predicate(ctx):
		if ctx.author.id == roxbot.owner:
			return True
		return commands.has_permissions(**perms)
	return commands.check(predicate)


def is_nsfw():
	"""A :func:`.check` that checks if the channel is a NSFW channel or a DM channel."""
	def pred(ctx):
		is_dm_channel = bool(isinstance(ctx.channel, discord.DMChannel))
		is_nsfw_guild_channel = bool(isinstance(ctx.channel, discord.TextChannel) and ctx.channel.is_nsfw())
		if is_nsfw_guild_channel:
			nsfw_enabled = bool(roxbot.guild_settings.get(ctx.guild)["nsfw"]["enabled"])
			return nsfw_enabled
		else:
			return is_dm_channel
	return commands.check(pred)
