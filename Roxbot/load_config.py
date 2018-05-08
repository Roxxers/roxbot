from enum import Enum
import configparser


settings = configparser.ConfigParser()
settings.read("Roxbot/settings/preferences.ini")

command_prefix = settings["Roxbot"]["Command_Prefix"]
token = settings["Roxbot"]["Token"]
owner = int(settings["Roxbot"]["OwnerID"])
tat_token = settings["Roxbot"]["Tatsumaki_Token"]


class EmbedColours(Enum):
	pink = 0xDEADBF
	yellow = 0xFDDF86
	blue = 0x6F90F5
	frog_green = 0x4C943D  # Used for FROGTIPS
	red = 0xe74c3c         # Used for on_error
	dark_red = 0x992d22    # Used for on_command_error


# REMEMBER TO UNCOMMENT THE GSS LINE, ROXIE

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
	"Roxbot.cogs.voice",
	#"Roxbot.cogs.gss"
]
