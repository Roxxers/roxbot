import configparser

settings = configparser.ConfigParser()
settings.read("config/preferences.ini")

command_prefix = settings["Roxbot"]["Command_Prefix"]
token = settings["Roxbot"]["Token"]
owner = settings["Roxbot"]["OwnerID"]