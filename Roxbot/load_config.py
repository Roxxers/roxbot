import configparser

settings = configparser.ConfigParser()
settings.read("Roxbot/preferences.ini")

command_prefix = settings["Roxbot"]["Command_Prefix"]
token = settings["Roxbot"]["Token"]
owner = int(settings["Roxbot"]["OwnerID"])
tat_token = settings["Roxbot"]["Tatsumaki_Token"]


__description__ = """RoxBot, A Discord Bot made by a filthy Mercy Main. Built with love (and discord.py) by Roxxers#7443.

[Github link](https://github.com/RainbowDinoaur/roxbot)
[Changelog](https://github.com/RainbowDinoaur/roxbot#v100)
[Found a bug or need to report an issue? Report it here](https://github.com/RainbowRoxxers/roxbot/issues/new)
[Say Thanks](https://saythanks.io/to/Roxxers)"""
__author__ = "Roxanne Gibson"
__version__ = "1.6.0"
embedcolour = 0xDEADBF

# IF YOU ARE TESTING OR NOT IN THE GSS DISCORD, REMOVE "cogs.gss" FROM THE LIST

cogs = [
	"Roxbot.cogs.admin",
	"Roxbot.cogs.customcommands",
	"Roxbot.cogs.fun",
	"Roxbot.cogs.joinleave",
	"Roxbot.cogs.nsfw",
	"Roxbot.cogs.reddit",
	"Roxbot.cogs.selfassign",
	"Roxbot.cogs.trivia",
	"Roxbot.cogs.twitch",
	"Roxbot.cogs.util",
	#"Roxbot.cogs.gss"
]
