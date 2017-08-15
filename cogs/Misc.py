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

        return await self.bot.send_file(ctx.message.channel, avaimg)

    @bot.command(pass_context=True)
    async def info(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.message.author
        name_disc = member.name + "#" + member.discriminator
        if member.game:
            if member.game.type:
                game = member.game.name
                desc = "Streaming "
            else:
                game = member.game.name
                desc = "Playing "
        else:
            desc = ""
            game = ""

        colour = member.colour.value
        avatar = member.avatar_url

        embed = discord.Embed(colour=colour, description=desc+game)
        embed.set_thumbnail(url=avatar)
        embed.set_author(name=name_disc, icon_url=avatar)

        embed.add_field(name="🤔", value="some of these properties have certain limits...")
        embed.add_field(name="😱", value="try exceeding some of them!")
        embed.add_field(name="🙄", value=" ")
        embed.add_field(name="<:thonkang:219069250692841473>", value="these last two", inline=True)
        embed.add_field(name="<:thonkang:219069250692841473>", value="are inline fields", inline=True)

        return await self.bot.say(embed=embed)

def setup(Bot):
    Bot.add_cog(Misc(Bot))