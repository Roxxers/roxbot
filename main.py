#!/usr/env python

import configparser

import discord
from discord.ext.commands import Bot

from config.config import Config
from cogs import cogs

__version__ = '0.3.6'
# TODO: make that constants file
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
    await bot.change_presence(game=discord.Game(name="v"+__version__), afk=False)
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


if __name__ == "__main__":
    bot.run(token)
