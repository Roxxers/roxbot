#!/usr/bin/env python3
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
import logging
import time
import traceback

import discord

import roxbot
from roxbot import db
from roxbot.scripts import JSONtoDB

# Sets up Logging
#discord_logger = logging.getLogger('discord')
#discord_logger.setLevel(logging.INFO)
#discord_logger.addHandler(roxbot.handler)




bot = roxbot.bot.Roxbot(
    command_prefix=roxbot.command_prefix,
    description=roxbot.__description__,
    owner_id=roxbot.owner,
    activity=discord.Game(name="v{}".format(roxbot.__version__), type=0),
    case_insensitive=True
)


@bot.event
async def on_ready():
    print("Logged in as: {}".format(roxbot.bot.term.fOKGREEN.format(str(bot.user))), end="\n\n")

    print("Guilds in: [{}]".format(len(bot.guilds)))
    for guild in bot.guilds:
        print(guild)

    roxbot.scripts.JSONtoDB.check_convert(bot.guilds)




@bot.event
async def on_guild_join(guild):
    db.populate_single_settings(bot)


@bot.event
async def on_guild_remove(guild):
    db.delete_single_settings(guild)


@bot.check
def check_blacklist(ctx):
    """Adds global check to the bot to check for a user being blacklisted."""
    return not bot.blacklisted(ctx.author)


@bot.command()
async def about(ctx):
    """
    Outputs info about RoxBot, showing up time, how to report issues, contents of roxbot.conf and credits.
    """
    owner = bot.get_user(roxbot.owner)
    em = discord.Embed(title="About Roxbot", colour=roxbot.EmbedColours.pink, description=roxbot.__description__)
    em.set_thumbnail(url=bot.user.avatar_url)
    em.add_field(name="Bot Version", value=roxbot.__version__)
    em.add_field(name="Discord.py version", value=discord.__version__)
    em.add_field(name="Owner", value=str(owner))
    em.add_field(name="Owner ID", value=roxbot.owner)
    em.add_field(name="Command Prefix", value=roxbot.command_prefix)
    em.add_field(name="Backup Enabled", value=roxbot.backup_enabled)
    if roxbot.backup_enabled:
        em.add_field(name="Backup Rate", value="{} Minutes".format(int(roxbot.backup_rate/60)))

    em.add_field(name="Author", value=roxbot.__author__)

    # Do time calc late in the command so that the time returned is closest to when the message is received
    uptimeflo = time.time() - start_time
    uptime = str(datetime.timedelta(seconds=uptimeflo))
    em.add_field(name="Current Uptime", value=str(uptime.split(".")[0]))
    em.set_footer(text="RoxBot is licensed under the MIT License")
    return await ctx.channel.send(embed=em)


if __name__ == "__main__":
    start_time = time.time()
    import threading
    from roxbot import webapp
    threading.Thread(target=webapp.app.app.run, kwargs={'debug': True,'use_reloader': False}).start()
    bot.run(roxbot.token)


