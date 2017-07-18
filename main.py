##############
# To-do List #
##############

# High Priority #
# TODO: Command Review, look at all commands and flesh them out. Maybe some randomised dialogue so that not every command has only one response. Make sure user experience feels nice.
# TODO: Also self delete timers.
# TODO: Full Docs on the commands and their use
# TODO: Complete rework of the commands. Moving to cog based commands again. Rework the code to be easier and cleaner.

# Mid Priority #
# TODO: Move away from using ID's for everthing. Maybe replace list with dict
# TODO: Admin tools - For commands already in and things like purge a chat
# TODO: On member role assign, welcome member using on_member_update

# Low Priority #
# TODO: Better help menu- AutoGen using <command>.help
# TODO: Overwatch stats - Using Overwatch-API lib
# TODO: Add check for no channel id when a module is enabled


import random
import configparser

import discord
from discord.ext.commands import Bot

from config import config
from cogs import cogs

__version__ = '0.3.0'


settings = configparser.ConfigParser()
settings.read('config/settings.ini')

token = settings["Credentials"]["Token"]
owner_id = settings["RoxBot"]["OwnerID"]
command_prefix = settings["RoxBot"]["CommandPrefix"]

bot = Bot(command_prefix=command_prefix)
con = config.Config(bot)


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

    em = discord.Embed(
        title="Welcome to {}!".format(member.server),
        description='Hey {}! Welcome to {}! Be sure to read the rules.'.format(member.mention, member.server),
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
