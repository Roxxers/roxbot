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


class AssortedGenderSounds(commands.Cog):
    """Custom Cog for the AssortedGenderSounds Discord Server."""
    def __init__(self, bot_client):
        self.bot = bot_client
        self.required_score = 2000
        self.days = 5
        self.logging_channel_id = 712934360600543253
        self.newbie_role_id = 450042170112475136
        self.selfie_role_id = 394939389823811584
        self.ags_id = 393764974444675073
        self.tat_token = roxbot.config["Tokens"]["Tatsumaki"]
        self.bot.add_listener(self.grab_objects, "on_ready")
        self.ags = None
        self.selfie_role = None
        self.newbie_role = None
        self.logging_channel = None

    async def cog_check(self, ctx):
        return ctx.guild.id == self.ags_id

    async def grab_objects(self):
        self.ags = self.bot.get_guild(self.ags_id)
        self.selfie_role = self.ags.get_role(self.selfie_role_id)
        self.newbie_role = self.ags.get_role(self.newbie_role_id)
        self.logging_channel = self.ags.get_channel(self.logging_channel_id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild == self.ags:
            await member.add_roles(self.newbie_role, reason="Auto-add role on join")
            await member.send("Welcome to AGS! If you're new here, please take the time to read our <#422514427263188993> and the <#396697172139180033> channel. Once you are ready, just make a post in <#450040463794241536> - if you're having any trouble, ask for a member of staff. We hope you have fun and enjoy the server <:hrtTrans:591277334926196736> <:hrtNonbinary:591245470165368839> <:hrtlgbtphilly:589153299266142218> <:hrtGenderqueer:591277330673172502> <:hrtAgender:591245404415459338>")

    async def tatsumaki_api_call(self, member, guild):
        base = "https://api.tatsumaki.xyz/"
        url = base + "guilds/" + str(guild.id) + "/members/" + str(member.id) + "/stats"
        return await roxbot.http.api_request(url, headers={"Authorization": self.tat_token})

    @commands.command()
    async def agree(self, ctx):
        try:
            return await ctx.author.remove_roles(self.newbie_role, reason="User has agreed the rules and has been given access to the server.")
        except discord.HTTPException:
            pass

    @commands.command(name="selfieperms")
    async def selfie_perms(self, ctx):
        """Requests the selfie perm role."""
        member = ctx.author

        data = await self.tatsumaki_api_call(member, ctx.guild)
        if data is None:
            return await ctx.send("Tatsumaki API call returned nothing. Maybe the API is down?")

        if self.selfie_role in member.roles:
            await member.remove_roles(self.selfie_role, reason="Requested removal of {0.name}".format(self.selfie_role))
            return await ctx.send("You already had {0.name}. It has now been removed.".format(self.selfie_role))

        time = datetime.datetime.now() - ctx.author.joined_at

        if time > datetime.timedelta(days=self.days) and int(data["score"]) >= self.required_score:
            await member.add_roles(self.selfie_role, reason="Requested {0.name}".format(self.selfie_role))
            await ctx.send("You now have the {0.name} role".format(self.selfie_role))
        else:
            return await ctx.send(
                "You do not meet the requirements for this role. You need at least {} score with <@!172002275412279296> and to have been in the server for {} days.".format(self.required_score, self.days)
            )


def setup(bot_client):
    bot_client.add_cog(AssortedGenderSounds(bot_client))
