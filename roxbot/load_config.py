from enum import IntEnum
import configparser


settings = configparser.ConfigParser()
settings.read("roxbot/settings/preferences.ini")

command_prefix = settings["Roxbot"]["Command_Prefix"]
token = settings["Roxbot"]["Token"]
owner = int(settings["Roxbot"]["OwnerID"])
tat_token = settings["Roxbot"]["Tatsumaki_Token"]


class EmbedColours(IntEnum):
	pink       = 0xDEADBF  # Roxbot Pink
	yellow     = 0xFDDF86  # Roxbot Yellow
	blue       = 0x6F90F5  # Roxbot Blue
	frog_green = 0x4C943D  # Used for FROGTIPS
	red        = 0xe74c3c  # Used for on_error
	dark_red   = 0x992d22  # Used for on_command_error
	triv_green = 0x1fb600  # Used for the correct answer in trivia
	gold       = 0xd4af3a  # Used for displaying the winner in trivia


# REMEMBER TO UNCOMMENT THE GSS LINE, ROXIE

cogs = [
	"roxbot.cogs.admin",
	"roxbot.cogs.customcommands",
	"roxbot.cogs.fun",
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
