# -*- coding: utf-8 -*-

# ______ _______   ________  _____ _____
# | ___ \  _  \ \ / /| ___ \|  _  |_   _|
# | |_/ / | | |\ V / | |_/ /| | | | | |
# |    /| | | |/   \ | ___ \| | | | | |
# | |\ \\ \_/ / /^\ \| |_/ /\ \_/ / | |
# \_| \_|\___/\/   \/\____/  \___/  \_/

# Roxbot, a lgbtq friendly Discord bot.

__title__ = "roxbot"
__author__ = "Roxanne Gibson"
__license__ = "MIT"
__copyright__ = "Copyright 2015-2017 Roxanne Gibson"
__version__ = "2.0.0"
__description__ = """RoxBot, a LGBTQ friendly Discord bot. Built with love (and discord.py) by Roxxers#7443.

[Github link](https://github.com/roxxers/roxbot)
[Changelog](https://github.com/roxxers/roxbot/blob/master/CHANGELOG.md)
[Found a bug or need to report an issue? Report it here](https://github.com/roxxers/roxbot/issues/new)
[Say Thanks](https://saythanks.io/to/Roxxers)"""

from roxbot import checks, http, guild_settings, converters, utils, roxbotfacts
from roxbot.exceptions import *
from roxbot.enums import EmbedColours
from roxbot.utils import blacklisted, log

import configparser

dev_mode = False

config = configparser.ConfigParser()
config.read("roxbot/settings/preferences.ini")

command_prefix = config["Roxbot"]["Command_Prefix"]
owner = int(config["Roxbot"]["OwnerID"])

token = config["Tokens"]["Discord"]
imgur_token = config["Tokens"]["Imgur"]

if config["Backups"]["enabled"] == "False":
	backup_enabled = False
else:
	backup_enabled = True
backup_rate = config["Backups"]["rate"] * 60  # Convert minutes to seconds


datetime_formatting = "{:%a %Y/%m/%d %H:%M:%S} UTC"

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
	#"roxbot.cogs.twitch",
	"roxbot.cogs.util",
	"roxbot.cogs.voice",
	#"roxbot.cogs.ags"
]

import logging
handler = logging.FileHandler(filename='roxbot.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger = logging.getLogger('roxbot')
logger.setLevel(logging.INFO)
logger.addHandler(handler)
