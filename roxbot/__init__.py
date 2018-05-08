from roxbot import checks, http, guild_settings
from roxbot.load_config import *
from roxbot.logging import log


def blacklisted(user):
	with open("roxbot/settings/blacklist.txt", "r") as fp:
		for line in fp.readlines():
			if str(user.id)+"\n" == line:
				return True
	return False


__description__ = """RoxBot, A Discord Bot made by a filthy Mercy Main. Built with love (and discord.py) by Roxxers#7443.

[Github link](https://github.com/RainbowDinoaur/roxbot)
[Changelog](https://github.com/RainbowDinoaur/roxbot#v100)
[Found a bug or need to report an issue? Report it here](https://github.com/RainbowRoxxers/roxbot/issues/new)
[Say Thanks](https://saythanks.io/to/Roxxers)"""
__author__ = "Roxanne Gibson"
__version__ = "1.7.0"
