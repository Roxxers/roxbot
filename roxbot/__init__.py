from roxbot import checks, http, guild_settings, converters, utils
from roxbot.enums import EmbedColours
from roxbot.logging import log
from roxbot.utils import blacklisted

import configparser


settings = configparser.ConfigParser()
settings.read("roxbot/settings/preferences.ini")

command_prefix = settings["Roxbot"]["Command_Prefix"]
token = settings["Roxbot"]["Token"]
owner = int(settings["Roxbot"]["OwnerID"])
tat_token = settings["Roxbot"]["Tatsumaki_Token"]


__description__ = """RoxBot, A Discord Bot made by a filthy Mercy Main. Built with love (and discord.py) by Roxxers#7443.

[Github link](https://github.com/Roxxers/roxbot)
[Changelog](https://github.com/Roxxers/roxbot/wiki/Changelog)
[Found a bug or need to report an issue? Report it here](https://github.com/Roxxers/roxbot/issues/new)
[Say Thanks](https://saythanks.io/to/Roxxers)"""
__author__ = "Roxanne Gibson"
__version__ = "1.8.0"


# REMEMBER TO UNCOMMENT THE GSS LINE, ROXIE

cogs = [
	"roxbot.cogs.admin",
	"roxbot.cogs.customcommands",
	"roxbot.cogs.fun",
	"roxbot.cogs.image",
	"roxbot.cogs.joinleave",
	"roxbot.cogs.nsfw",
	"roxbot.cogs.reddit",
	"roxbot.cogs.selfassign",
	"roxbot.cogs.trivia",
	"roxbot.cogs.twitch",
	"roxbot.cogs.util",
	"roxbot.cogs.voice",
	#"roxbot.cogs.gss"
]
