

from pony.orm import *

import discord
from discord.ext import commands

from roxbot.db import *


class Leveleing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def define_tables(self, db):
        class Users(db.Entity):
            id = PrimaryKey(int, size=64)
            pronouns = Optional(str)
            bio = Optional(str)
            guild_leaderboards = Set("LvlGuildLeaderboardEntries")
            currency = Required(int, size=32, default=0)

        class LvlGuildLeaderboardEntries(db.Entity):
            user = Required(Users)
            score = Required(int, size=32, default=0)
            guild_id = Required(int, size=64)

    @commands.Cog.listener()
    async def on_ready(self):
        # TODO: Output explaining this taking forever on new versions of the bot
        for user in self.bot.users:
            try:
                with db_session:
                    db.Users(id=user.id)
            except TransactionIntegrityError:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.command()
    async def points(self, ctx):
        pass




def setup(bot):
    bot.add_cog(Leveleing(bot))