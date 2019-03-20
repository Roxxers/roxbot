# -*- coding: utf-8 -*-

# ____           _           _
# |  _ \ _____  _| |__   ___ | |_
# | |_) / _ \ \/ / '_ \ / _ \| __|
# |  _ < (_) >  <| |_) | (_) | |_
# |_| \_\___/_/\_\_.__/ \___/ \__|

# Roxbot: An inclusive modular multi-purpose Discord bot.

__title__ = "roxbot"
__author__ = "Roxanne Gibson"
__license__ = "MIT"
__copyright__ = "Copyright 2015-2017 Roxanne Gibson <me@roxxers.xyz>"
__version__ = "2.2.0"
__description__ = """Roxbot: An inclusive modular multi-purpose Discord bot. Built with love (and discord.py) by Roxxers#7443.

Roxbot is designed be a multi-purpose bot and provide many different services for users and moderators alike with a focus on customisability. 

Roxbot also has a focus on being inclusive and being fun for all kinds of people. Roxbot is a bot written by a queer woman with the lgbt community in mind. 

[Github link](https://github.com/roxxers/roxbot)
[Changelog](https://github.com/roxxers/roxbot/blob/master/CHANGELOG.md)
[Docs](https://roxxers.github.io/roxbot/)
[Found a bug or need to report an issue? Report it here](https://github.com/roxxers/roxbot/issues/new)
"""

from .enums import EmbedColours
from .config import config
from .exceptions import UserError, CogSettingDisabled

from . import checks, http, converters, utils, roxbotfacts, exceptions, db


command_prefix = config["Roxbot"]["Command_Prefix"]
owner = int(config["Roxbot"]["OwnerID"])
token = config["Tokens"]["Discord"]
imgur_token = config["Tokens"]["Imgur"]

if config["Backups"]["enabled"] == "False":
    backup_enabled = False
else:
    backup_enabled = True
backup_rate = int(config["Backups"]["rate"]) * 60  # Convert minutes to seconds

dev_mode = False
datetime = "{:%a %Y/%m/%d %H:%M:%S} UTC"

cog_list = [
    "roxbot.cogs.admin",
    "roxbot.cogs.customcommands",
    "roxbot.cogs.fun",
    "roxbot.cogs.image",
    "roxbot.cogs.joinleave",
    "roxbot.cogs.nsfw",
    "roxbot.cogs.reddit",
    "roxbot.cogs.selfassign",
    "roxbot.cogs.trivia",
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
