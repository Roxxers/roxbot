import configparser

settings = configparser.ConfigParser()
settings.read("Roxbot/preferences.ini")

command_prefix = settings["Roxbot"]["Command_Prefix"]
token = settings["Roxbot"]["Token"]
owner = int(settings["Roxbot"]["OwnerID"])
tat_token = settings["Roxbot"]["Tatsumaki_Token"]
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
	"Roxbot.cogs.voice",
	#"Roxbot.cogs.gss"
]
