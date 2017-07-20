#!/usr/env python

import configparser

import discord
from discord.ext.commands import Bot

from config.config import Config
from cogs import cogs

__version__ = '0.3.3'

settings = configparser.ConfigParser()
settings.read('config/settings.ini')

token = settings["Credentials"]["Token"]
owner_id = settings["RoxBot"]["OwnerID"]
command_prefix = settings["RoxBot"]["CommandPrefix"]

bot = Bot(command_prefix=command_prefix)
con = Config(bot)


def blacklisted(user):
    with open("config/blacklist.txt", "r") as fp:
        for line in fp.readlines():
            if user.id+"\n" == line:
                return True
        return False


@bot.event
async def on_ready():
    # TODO: First part needs to be moved to wait_until_ready
    con.config_errorcheck()
    print("Discord.py version: "+discord.__version__)
    print("Client logged in\n")
    await bot.change_presence(game=discord.Game(name=__version__), afk=False)
    print("Cods loaded:")
    for cog in cogs:
        bot.load_extension(cog)
        print("{}".format(cog))
    print("")
    print("Servers I am currently in:")
    for server in bot.servers:
        print(server)
    print("")


@bot.event
async def on_message(message):
    if blacklisted(message.author):
        return
    else:
        return await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    """
    Greets users when they join a server. 
    
    :param member: 
    :return: 
    """
    print(con.serverconfig[member.server.id]["greets"]["enabled"])
    if not con.serverconfig[member.server.id]["greets"]["enabled"]:
        return
    if con.serverconfig[member.server.id]["greets"]["custom-message"]:
        message = con.serverconfig[member.server.id]["greets"]["custom-message"]
    else:
        message = con.serverconfig[member.server.id]["greets"]["default-message"]
    # TODO: Maybe thumbnail for the embed
    em = discord.Embed(
        title="Welcome to {}!".format(member.server),
        description='Hey {}! Welcome to **{}**! {}'.format(member.mention, member.server, message),
        colour=0xDEADBF)

    if con.serverconfig[member.server.id]["greets"]["welcome-channel"]:
        channel = discord.Object(con.serverconfig[member.server.id]["greets"]["welcome-channel"])
    else:
        channel = member.server.default_channel
    return await bot.send_message(channel,embed=em)


@bot.event
async def on_member_remove(member):
    if not con.serverconfig[member.server.id]["goodbyes"]["enabled"]:
        return
    else:
        return await bot.send_message(member.server,embed=discord.Embed(
            description="{}#{} has left or been beaned.".format(member.name, member.discriminator), colour=0xDEADBF))


if __name__ == "__main__":
    bot.run(token)
