
import random

import roxbot

import discord
from discord.ext import commands


class Fun(commands.Cog):
    """
    Wordplay provides many text editing commands to make your shitposts more creative... sorta.
    Warning: This cog is not screen reader safe. Use with caution.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["za"])
    async def zalgo(self, ctx, *, text):
        """
        Sends text to the nether and returns it back to you ̭҉̭̭ͭi̭͎̭ṋ̭̀҈̭̭̋ ̭͉̭z̭̩̭a̭̭̽ḽ̦̭g̭̞̭o̭̤̭ ̭̭͑f̭̻̭o̭̭͢r̭̭̀m̭̭ͮ

        Example:
            # Convert "Hello World" to zalgo.
            ;zalgo Hello World
        """
        intensity = 10
        zalgo_chars = [*[chr(i) for i in range(0x0300, 0x036F + 1)], *[u'\u0488', u'\u0489']]
        zalgoised = []
        for letter in text:
            zalgoised.append(letter)
            zalgo_num = random.randint(0, intensity) + 1
            for _ in range(zalgo_num):
                zalgoised.append(random.choice(zalgo_chars))
        response = random.choice(zalgo_chars).join(zalgoised)
        output = await ctx.send(response)

        if isinstance(ctx.channel, discord.TextChannel):
            await self.bot.log(
                ctx.guild,
                "zalgo",
                User=ctx.author,
                User_ID=ctx.author.id,
                Output_Message_ID=output.id,
                Channel=ctx.channel,
                Channel_Mention=ctx.channel.mention,
                Time=roxbot.datetime.format(ctx.message.created_at)
            )

    @commands.command(aliases=["ae", "aesthetic"])
    async def aesthetics(self, ctx, *, text):
        """Converts text to be more  a e s t h e t i c

        Example:
            # Convert "Hello World" to fixed-width text.
            ;ae Hello World
        """
        wide_map = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))  # Create dict with fixed width equivalents for chars
        wide_map[0x20] = 0x3000  # replace space with 'IDEOGRAPHIC SPACE'
        converted = str(text).translate(wide_map)
        output = await ctx.send(converted)

        if isinstance(ctx.channel, discord.TextChannel):
            await self.bot.log(
                ctx.guild,
                "aesthetics",
                User=ctx.author,
                User_ID=ctx.author.id,
                Output_Message_ID=output.id,
                Channel=ctx.channel,
                Channel_Mention=ctx.channel.mention,
                Time=roxbot.datetime.format(ctx.message.created_at)
            )

    @commands.command(aliases=["bw", "backward"])
    async def backwards(self, ctx, *, text):
        """
        Makes all of your text go sdrawkcab!backwards
        Example:
            # Make "Hello World" be spelt backwards.
            ;bw Hello World
        """
        new_string = ""
        old_string = list(text)
        for x in old_string[::-1]:
            new_string += x
        output = await ctx.send(new_string)

        if isinstance(ctx.channel, discord.TextChannel):
            await self.bot.log(
                ctx.guild,
                "aesthetics",
                User=ctx.author,
                User_ID=ctx.author.id,
                Output_Message_ID=output.id,
                Channel=ctx.channel,
                Channel_Mention=ctx.channel.mention,
                Time=roxbot.datetime.format(ctx.message.created_at)
            )


def setup(bot):
    bot.add_cog(Fun(bot))
