#!/usr/env python

##############
# To-do List #
##############

# High Priority #
# TODO: Fix Config Bug

# Mid Priority #
# TODO: Move away from using ID's for everything. Maybe replace list with dict
# TODO: Admin tools - For commands already in and things like purge a chat
# TODO: On member role assign, welcome member using on_member_update

# Low Priority #
# TODO: Command Review, look at all commands and flesh them out. Make sure user experience feels nice
# TODO: Better help menu- AutoGen using <command>.help
# TODO: Overwatch stats - Using Overwatch-API lib
# TODO: Add check for no channel id when a module is enabled
# TODO: Maybe some randomised dialogue so that not every command has only one response.

import configparser

import discord
from discord.ext.commands import Bot

from config.config import Config
from cogs import cogs

__version__ = '0.3.0'

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
    await bot.change_presence(game=discord.Game(name="v0.3.0_Testing"), status=discord.Status.dnd, afk=False)
    for cog in cogs:
        bot.load_extension(cog)
        print(f"{cog} Cog added")
    print(discord.__version__)
    print("Client logged in\n")
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
    if not con.serverconfig[member.server.id]["greets"]["enabled"]:
        return
    print("Passes Enabled Check")
    if con.serverconfig[member.server.id]["greets"]["custom-message"]:
        message = con.serverconfig[member.server.id]["greets"]["custom-message"]
    else:
        message = con.serverconfig[member.server.id]["greets"]["default-message"]
    print("passed message check")
    em = discord.Embed(
        title="Welcome to {}!".format(member.server),
        description='Hey {}! Welcome to **{}**! {}'.format(member.mention, member.server, message),
        colour=0xDEADBF)

    if con.serverconfig[member.server.id]["greets"]["welcome-channel"]:
        channel = discord.Object(con.serverconfig[member.server.id]["greets"]["welcome-channel"])
    else:
        channel = member.server.default_channel
    print("passed channel getting")
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
