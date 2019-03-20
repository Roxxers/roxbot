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


import datetime

import discord
from discord.ext import commands

import roxbot
from roxbot.db import *


class AdminSingle(db.Entity):
    warning_limit = Required(int, default=0)
    guild_id = Required(int, unique=True, size=64)


class AdminWarnings(db.Entity):
    user_id = Required(int, size=64)
    warned_by = Required(int, size=64)
    warning = Optional(str)
    date = Required(datetime.datetime, unique=True)
    guild_id = Required(int, size=64)


class Admin(commands.Cog):
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
        self.autogen_db = AdminSingle

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command()
    async def slowmode(self, ctx, seconds: int):
        """Puts the channel in slowmode. Users with manage_channel or manage_messages permissions will not be effected.

        Options:
            - `seconds` - Has to be between 0 - 120. This will set the timeout a user receives once they send a message in this channel. If 0, Roxbot will disable slowmode.

        Examples:
            # Set slowmode to 30 seconds
            ;slowmode 30
            # Turn slowmode off
            ;slowmode 0
        """
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
    async def purge(self, ctx, limit=0, *, author: roxbot.converters.User = None):
        """Purges the text channel the command is execture in. You can specify a certain user to purge as well.

        Options:
            - `limit` - This the the amount of messages Roxbot will take from the chat and purge. Note: This **does not** mean the amount that will be purged. Limit is the amount of messages Roxbot will look at. If a user is given, it will only delete messages from that user in that list of messages.
            - `USER` - A name, ID, or mention of a user. If the user has left the guild, this **has** to be the ID.

        Examples:
            # Delete 20 messages from the chat
            ;purge 20
            # Take 20 messages, and delete any message in it by user @Spammer
            ;purge 20 @Spammer
        """
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
        """The warn command group allows Discord moderators to warn users and log them within the bot.

        The command group also supports setting limits to warn mods if a user has been warned over a certain threshold.
        """
        if ctx.invoked_subcommand is None:
            raise commands.CommandNotFound("Subcommand '{}' does not exist.".format(ctx.subcommand_passed))

    @warn.command()
    async def add(self, ctx, user: discord.User = None, *, warning=""):
        """Adds a warning to a user.

        Options:
            - `USER` - A name, ID, or mention of a user.
            - `warning` - OPTIONAL. A reason for the warning. This supports markdown formatting.

        Example:
            # Add warning to user @Roxbot for being a meanie
            ;warn add @Roxbot "for being a meanie"
        """

        # Warning in the settings is a dictionary of user ids. The user ids are equal to a list of dictionaries.
        with db_session:
            warning_limit = AdminSingle.get(guild_id=ctx.guild.id).warning_limit
            user_warnings = select(w for w in AdminWarnings if w.user_id == user.id and w.guild_id == ctx.guild.id)[:]
        amount_warnings = len(user_warnings)

        warn_limit = 10
        if amount_warnings > warn_limit:
            embed = discord.Embed(description=self.WARN_WARN_ADD_LIMIT_REACHED.format(warn_limit), colour=roxbot.EmbedColours.red)
            return await ctx.send(embed=embed)

        with db_session:
            AdminWarnings(user_id=user.id, warned_by=ctx.author.id, date=datetime.datetime.utcnow(), warning=warning, guild_id=ctx.guild.id)

        if amount_warnings >= warning_limit > 0:
            await ctx.author.send(self.OK_WARN_ADD_USER_LIMIT_DM.format(str(user), amount_warnings, warning_limit))

        embed = discord.Embed(description=self.OK_WARN_ADD.format(str(user)), colour=roxbot.EmbedColours.pink)
        return await ctx.send(embed=embed)

    @warn.command()
    async def list(self, ctx, *, user: roxbot.converters.User = None):
        """Lists all warning in this guild or all the warnings for one user.

        Options:
        -	 `USER` - OPTIONAL. A name, ID, or mention of a user.

        Examples:
            # List all warnings in the guild
            ;warn list
            # List all warnings for @Roxbot
            ;warn list @Roxbot
        """
        if user is None:
            paginator = commands.Paginator()
            warnings = {}
            with db_session:
                for warning in select(warn for warn in AdminWarnings if warn.guild_id == ctx.guild.id)[:]:
                    if warning.user_id not in warnings:
                        warnings[warning.user_id] = []
                    else:
                        warnings[warning.user_id].append(warning)

            for u, warning in warnings.items():
                member_obj = discord.utils.get(ctx.guild.members, id=u)
                if member_obj:
                    paginator.add_line("{}: {} Warning(s)".format(str(member_obj), len(warnings[u])))
                else:
                    paginator.add_line("{}: {} Warning(s)".format(u, len(warnings[u])))
            # This is in case we have removed some users from the list.

            if not paginator.pages:
                embed = discord.Embed(description=self.OK_WARN_LIST_NO_WARNINGS, colour=roxbot.EmbedColours.orange)
                return await ctx.send(embed=embed)

            for page in paginator.pages:
                return await ctx.send(page)
        else:
            with db_session:
                user_warnings = select(w for w in AdminWarnings if w.user_id == user.id and w.guild_id == ctx.guild.id).order_by(AdminWarnings.date)[:]

            if not user_warnings:
                embed = discord.Embed(description=self.OK_WARN_LIST_USER_NO_WARNINGS, colour=roxbot.EmbedColours.orange)
                return await ctx.send(embed=embed)

            em = discord.Embed(title="Warnings for {}".format(str(user)), colour=roxbot.EmbedColours.pink)
            em.set_thumbnail(url=user.avatar_url)

            x = 1
            for warning in user_warnings:
                try:
                    warned_by = str(ctx.guild.get_member(warning.warned_by))
                    if warned_by is None:
                        warned_by = str(await self.bot.fetch_user(warning.warned_by))
                except discord.ext.commands.CommandInvokeError:
                    warned_by = warning.warned_by
                date = datetime.datetime.strftime(warning.date, roxbot.datetime.strip("{:} UTC")+" UTC")
                em.add_field(name="Warning %s" % x, value="Warned by: {}\nTime: {}\nReason: {}".format(warned_by, date, warning.warning))
                x += 1
            return await ctx.send(embed=em)

    @warn.command()
    async def remove(self, ctx, user: roxbot.converters.User, index=None):
        """Removes one or all of the warnings for a user.

        Options:=
            - `USER` - A name, ID, or mention of a user.
            - `index` - OPTIONAL. The index of the single warning you want to remove.

        Examples:
            # Remove all warnings for Roxbot
            ;warn remove Roxbot
            # Remove warning 2 for Roxbot
            ;warn remove Roxbot 2
        """
        with db_session:
            if index:
                try:
                    index = int(index) - 1
                    query = select(w for w in AdminWarnings if w.user_id == user.id and w.guild_id == ctx.guild.id)
                    if query:
                        user_warnings = query[:]
                    else:
                        raise KeyError
                    user_warnings[index].delete()

                    embed = discord.Embed(description=self.OK_WARN_REMOVE_REMOVED_WARNING.format(index+1, str(user)), colour=roxbot.EmbedColours.pink)
                    return await ctx.send(embed=embed)

                except Exception as e:
                    embed = discord.Embed(colour=roxbot.EmbedColours.red)
                    if isinstance(e, IndexError):
                        embed.description = self.ERROR_WARN_REMOVE_INDEXERROR.format(len(user_warnings))
                    elif isinstance(e, KeyError):
                        embed.description = self.WARN_WARN_REMOVE_USER_NOT_FOUND.format(str(user))
                    elif isinstance(e, ValueError):
                        embed.description = self.ERROR_WARN_REMOVE_VALUEERROR
                    else:
                        raise e
                    return await ctx.send(embed=embed)
            else:
                query = select(w for w in AdminWarnings if w.user_id == user.id and w.guild_id == ctx.guild.id)
                if query.exists():
                    delete(w for w in AdminWarnings if w.user_id == user.id and w.guild_id == ctx.guild.id)
                    embed = discord.Embed(description=self.OK_WARN_REMOVE_REMOVED_WARNINGS.format(str(user)), colour=roxbot.EmbedColours.pink)
                    return await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=self.WARN_WARN_REMOVE_USER_NOT_FOUND.format(str(user)), colour=roxbot.EmbedColours.red)
                    return await ctx.send(embed=embed)

    @commands.bot_has_permissions(ban_members=True)
    @warn.command()
    async def prune(self, ctx, dry_run=0):
        """Prunes the warnings of any banned users.
        You can add a 1 at the end to dryrun the command. This will show you how many would be deleted without deleting them.

        Options:
            - `dryrun` - Add `1` to the end of the command to do a dryrun of the prune command.

        Examples:
            # Prune the warnings of banned users in this guild
            ;warn prune
            # Dryrun the prune command to see how many warnings would be removed
            ;warn prune 1
        """
        x = 0
        for ban in await ctx.guild.bans():
            with db_session:
                query = select(w for w in AdminWarnings if w.user_id == ban.user.id and w.guild_id == ctx.guild.id)
                if query.exists():
                    if dry_run == 0:
                        query.delete()
                    x += 1
        embed = discord.Embed(description=self.OK_WARN_PRUNE_PRUNED.format(x), colour=roxbot.EmbedColours.pink)
        return await ctx.send(embed=embed)

    @warn.command(aliases=["sl", "setlimit"])
    async def set_limit(self, ctx, number_of_warnings: int):
        """
        Sets the limit for how many warnings a user can get before mod's are notified.

        Example: if 3 is set, on the third warning, mods will be DM'd. If this is set to 0, DM's will be disabled.
        """
        if number_of_warnings < 0:
            raise commands.BadArgument(self.ERROR_WARN_SL_NEG)

        with db_session:
            guild_settings = AdminSingle.get(guild_id=ctx.guild.id)
            guild_settings.warning_limit = number_of_warnings
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
        """Kicks the mentioned user with the ability to give a reason.

        Requires the Kick Members permission.

        Options:
            - `USER` - A name, ID, or mention of a user.
            - `reason` - OPTIONAL. A short reason for the kicking.

        Examples:
            # Kick user BadUser
            ;kick @BadUser
            # Kick user Roxbot for being a meanie
            ;kick Roxbot "for being a meanie"
        """
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
        """Bans the mentioned user with the ability to give a reason.

        Requires the Ban Members permission.

        Options:
            - `USER` - A name, ID, or mention of a user.
            - `reason` - OPTIONAL. A short reason for the banning.

        Examples:
            # Ban user BadUser
            ;ban @BadUser
            # Ban user Roxbot for being a meanie
            ;ban Roxbot "for being a meanie"
        """
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
        """Unbans the mentioned user with the ability to give a reason.

        Requires the Ban Members permission.

        Options:
            - `user_id` - The ID of a banned user.
            - `reason` - OPTIONAL. A short reason for the unbanning.

        Examples:
            # Unban user with ID 478294672394
            ;unban 478294672394
        """
        ban = await ctx.guild.fetch_ban(member)
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
