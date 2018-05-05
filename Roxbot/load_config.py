import configparser

settings = configparser.ConfigParser()
settings.read("Roxbot/settings/preferences.ini")

command_prefix = settings["Roxbot"]["Command_Prefix"]
token = settings["Roxbot"]["Token"]
owner = int(settings["Roxbot"]["OwnerID"])
tat_token = settings["Roxbot"]["Tatsumaki_Token"]
embedcolour = 0xDEADBF

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
