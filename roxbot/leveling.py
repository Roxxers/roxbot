

import random
import asyncio
from pony.orm import *

import discord
from discord.ext import commands

from roxbot.db import *


class Leveleing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_talkers = {}
        self.bot.add_listener(self.populate_dicts, "on_ready")

    def define_tables(self, database):
        class Users(database.Entity):
            id = PrimaryKey(int, size=64)
            pronouns = Optional(str)
            bio = Optional(str)
            guild_leaderboards = Set("LevelingLBEntries", cascade_delete=True)
            currency = Required(int, size=64, default=0)

        class LevelingLBEntries(database.Entity):
            user = Required(Users)
            points = Required(int, size=64, default=0)
            guild_id = Required(int, size=64)
            composite_key(user, guild_id)

    async def populate_dicts(self):
        for guild in self.bot.guilds:
            self.recent_talkers[guild.id] = {}

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.recent_talkers[guild.id] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # TODO: Output explaining this taking forever on new versions of the bot
        for user in self.bot.users:
            try:
                with db_session:
                    db.Users(id=user.id)
            except TransactionIntegrityError:
                pass
        for guild in self.bot.guilds:
            for member in guild.members:
                try:
                    with db_session:
                        user = db.Users.get(id=member.id)
                        db.LevelingLBEntries(user=user, guild_id=guild.id)
                except TransactionIntegrityError:
                    pass

    @commands.Cog.listener()
    async def on_message(self, message):
        async def remove_recent_talker_entry(author):
            await asyncio.sleep(60)
            del self.recent_talkers[author.guild.id][author.id]

        author = message.author
        guild = message.guild

        if self.bot.blacklisted(author):
            return
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return
        if author.id in self.recent_talkers[guild.id]:
            return

        self.recent_talkers[guild.id][author.id] = True
        points_awarded = random.randint(1, 11)
        currency_awarded = random.randint(1, 11)
        with db_session:
            user = db.Users.get(id=author.id)
            entry = db.LevelingLBEntries.get(user=user, guild_id=guild.id)

            user.currency += currency_awarded
            entry.points += points_awarded

        self.bot.loop.create_task(remove_recent_talker_entry(author))

    @commands.command()
    async def points(self, ctx):
        with db_session:
            user = db.Users.get(id=ctx.author.id)
            entry = db.LevelingLBEntries.get(user=user, guild_id=ctx.guild.id)
        await ctx.send(entry.points)


def setup(bot):
    bot.add_cog(Leveleing(bot))
