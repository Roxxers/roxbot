import os
import aiohttp
import discord
from discord.ext.commands import bot

class Misc():
    def __init__(self, Bot):
        self.bot = Bot

    @bot.command(pass_context=True)
    async def avatar(self, ctx, user: discord.User = None):
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif not user:
            user = ctx.message.author

        url = user.avatar_url
        avaimg = 'avaimg.webp'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as img:
                with open(avaimg, 'wb') as f:
                    f.write(await img.read())
        with open(avaimg, 'rb') as f:
            await self.bot.send_file(ctx.message.channel, f.read())
        os.remove(avaimg)

def setup(Bot):
    Bot.add_cog(Misc(Bot))