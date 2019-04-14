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


import asyncio
import discord
from discord.ext import commands

from pony.orm import db_session, select

import roxbot
from roxbot.db import db


class term:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

    fHEADER    =  HEADER    + "{}" + ENDC
    fOKBLUE    =  OKBLUE    + "{}" + ENDC
    fOKGREEN   =  OKGREEN   + "{}" + ENDC
    fWARNING   =  WARNING   + "{}" + ENDC
    fFAIL      =  FAIL      + "{}" + ENDC
    fBOLD      =  BOLD      + "{}" + ENDC
    fUNDERLINE =  UNDERLINE + "{}" + ENDC

    seperator = "================================"

    title = """ ____           _           _   
|  _ \ _____  _| |__   ___ | |_ 
| |_) / _ \ \/ / '_ \ / _ \| __|
|  _ < (_) >  <| |_) | (_) | |_ 
|_| \_\___/_/\_\_.__/ \___/ \__|
"""


class Roxbot(commands.Bot):
    """Modified client for Roxbot"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, *args, **kwargs):

        print(term.fHEADER.format(term.fBOLD.format(term.title)))

        print("Roxbot version:       " + term.fOKBLUE.format(roxbot.__version__))
        print("Discord.py version:   " + term.fOKBLUE.format(discord.__version__))

        print(term.seperator)

        print("Loading core...", end="\r")

        self.load_extension("roxbot.core")
        self.load_extension("roxbot.leveling")
        print("Loaded core.py")
        print(term.seperator)

        # Load Extension Cogs
        print("Cogs Loaded:")
        for cog in roxbot.cog_list:
            try:
                self.load_extension(cog)
                print(cog.split(".")[2])
            except ImportError:
                print("{} FAILED TO LOAD. MISSING REQUIREMENTS".format(cog.split(".")[2]))

        # DB setup

        for name, cog in self._cogs.items():
            try:
                # Define all tables in cogs
                cog.define_tables(db)
            except AttributeError:
                pass

        db.generate_mapping(create_tables=True)
        self.loop.create_task(roxbot.db.populate_db(self))

        print(term.seperator)
        print("Client logging in...", end="\r")
        return super().run(*args, **kwargs)

    @staticmethod
    def blacklisted(user):
        """Checks if given user is blacklisted from the bot.
        Params
        =======
        user: discord.User

        Returns
        =======
        If the user is blacklisted: bool"""
        with db_session:
            return select(u for u in db.Blacklist if u.user_id == user.id).exists()

    async def delete_option(self, message, delete_emoji=None, timeout=20):
        """Utility function that allows for you to add a delete option to the end of a command.
        This makes it easier for users to control the output of commands, esp handy for random output ones.

        Params
        =======
        message: discord.Message
            Output message from Roxbot
        delete_emoji: discord.Emoji or str if unicode emoji
            Used as the reaction for the user to click on.
        timeout: int (Optional)
            Amount of time in seconds for the bot to wait for the reaction. Deletes itself after the timer runes out.
            Set to 20 by default
        """
        if not delete_emoji:
            delete_emoji = "❌"

        def check(r, u):
            return str(r) == str(delete_emoji) and u != message.author and r.message.id == message.id

        await message.add_reaction(delete_emoji)

        try:
            await self.wait_for("reaction_add", timeout=timeout, check=check)
            await message.remove_reaction(delete_emoji, self.user)
            try:
                await message.remove_reaction(delete_emoji, message.author)
            except discord.Forbidden:
                pass
            await message.edit(content="{} requested output be deleted.".format(message.author), embed=None)
        except asyncio.TimeoutError:
            await message.remove_reaction(delete_emoji, self.user)

    async def log(self, guild, command_name, **kwargs):
        """Logs activity internally for Roxbot. Will only do anything if the server enables internal logging.

        This is mostly used for logging when certain commands are used that can be an issue for admins. Esp when Roxbot outputs
        something that could break the rules, then deletes their message.

        Params
        =======
        guild: discord.Guild
            Used to check if the guild has logging enabled
        channel: discord.TextChannel
        command_name: str
        kwargs: dict
            All kwargs and two other params will be added to the logging embed as fields, allowing you to customise the output

        """
        if guild:
            with db_session:
                logging = db.LoggingSingle.get(guild_id=guild.id)
            if logging.enabled and logging.logging_channel_id:
                channel = self.get_channel(logging.logging_channel_id)
                embed = discord.Embed(title="{} command logging".format(command_name), colour=roxbot.EmbedColours.pink)
                for key, value in kwargs.items():
                    embed.add_field(name=key, value=value)
                return await channel.send(embed=embed)
