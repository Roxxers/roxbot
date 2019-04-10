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


import typing
from pony import orm

import discord
from discord.ext import commands

import roxbot
from roxbot.db import *


class JoinLeave(commands.Cog):
    """JoinLeave is a cog that allows you to create custom welcome and goodbye messages for your Discord server. """

    DEFAULT_MESSAGE = "Be sure to read the rules."

    def __init__(self, bot_client):
        self.bot = bot_client

    def define_tables(self, db):
        class JoinLeaveSingle(db.Entity):
            greets_enabled = orm.Required(bool, default=False)
            goodbyes_enabled = orm.Required(bool, default=False)
            greets_channel_id = orm.Optional(int, nullable=True, size=64)
            goodbyes_channel_id = orm.Optional(int, nullable=True, size=64)
            greets_custom_message = orm.Optional(str, nullable=True)
            guild_id = orm.Required(int, size=64, unique=True)

        self.autogen_db = db.JoinLeaveSingle

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Greets users when they join a server.
        """
        if member == self.bot.user:
            return
        with db_session:
            settings = db.JoinLeaveSingle.get(guild_id=member.guild.id)

        if not settings.greets_enabled:
            return

        message = settings.greets_custom_message or self.DEFAULT_MESSAGE

        em = discord.Embed(
            title="Welcome to {}!".format(member.guild),
            description='Hey {}! Welcome to **{}**! {}'.format(member.mention, member.guild, message),
            colour=roxbot.EmbedColours.pink)
        em.set_thumbnail(url=member.avatar_url)

        channel = member.guild.get_channel(settings.greets_channel_id)
        return await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        The same but the opposite
        """
        if member == self.bot.user:
            return
        with db_session:
            settings = db.JoinLeaveSingle.get(guild_id=member.guild.id)
        if settings.goodbyes_enabled:
            try:
                channel = member.guild.get_channel(settings.goodbyes_channel_id)
                return await channel.send(embed=discord.Embed(
                    description="{}#{} has left or been beaned.".format(member.name, member.discriminator), colour=roxbot.EmbedColours.pink))
            except AttributeError:
                pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Cleans up settings on removal of stored IDs."""
        with db_session:
            settings = db.JoinLeaveSingle.get(guild_id=channel.guild.id)
            if channel.id == settings.greets_channel_id:
                settings.greets_channel_id = None
            if channel.id == settings.goodbyes_channel_id:
                settings.goodbyes_channel_id = None

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def greets(self, ctx, setting, channel: typing.Optional[discord.TextChannel] = None, *, text = ""):
        """Edits settings for the Welcome Messages

        Options:
            enable/disable: Enable/disables greet messages.
            channel: Sets the channel for the message to be posted in. If no channel is provided, it will default to the channel the command is executed in.
            message: Specifies a custom message for the greet messages.

        Example:
            Enable greet messages, set the channel to the current one, and set a custom message to be appended.
            `;greets enable`
            `;greets message "Be sure to read the rules and say hi! :wave:"`
            `;greets channel` # if no channel is provided, it will default to the channel the command is executed in.
        """
        setting = setting.lower()
        with db_session:
            settings = db.JoinLeaveSingle.get(guild_id=ctx.guild.id)
            if setting == "enable":
                settings.greets_enabled = True
                await ctx.send("'greets' was enabled!")

            elif setting == "disable":
                settings.greets_enabled = False
                await ctx.send("'greets' was disabled :cry:")

            elif setting in ("channel", "greet-channel"):
                channel = channel or ctx.channel
                settings.greets_channel_id = channel.id
                await ctx.send("Set greets channel to {}".format(channel.mention))

            elif setting in ("message", "custom-message"):
                settings.greets_custom_message = text
                await ctx.send("Custom message set to '{}'".format(text))

            else:
                return await ctx.send("No valid option given.")

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def goodbyes(self, ctx, setting, *, channel: typing.Optional[discord.TextChannel] = None):
        """Edits settings for the goodbye messages.

        Options:
            enable/disable: Enable/disables goodbye messages.
            channel: Sets the channel for the message to be posted in. If no channel is provided, it will default to the channel the command is executed in.

        Example:
            Enable goodbye messages, set the channel one called `#logs`
            `;goodbyes enable`
            `;goodbyes channel #logs`
        """
        setting = setting.lower()
        with db_session:
            settings = db.JoinLeaveSingle.get(guild_id=ctx.guild.id)
            if setting == "enable":
                settings.goodbyes_enabled = True
                await ctx.send("'goodbyes' was enabled!")
            elif setting == "disable":
                settings.goodbyes_enabled = False
                await ctx.send("'goodbyes' was disabled :cry:")
            elif setting in ("channel", "goodbye-channel"):
                channel = channel or ctx.channel
                settings.goodbyes_channel_id = channel.id
                await ctx.send("Set goodbye channel to {}".format(channel.mention))
            else:
                return await ctx.send("No valid option given.")

def setup(bot_client):
    bot_client.add_cog(JoinLeave(bot_client))
