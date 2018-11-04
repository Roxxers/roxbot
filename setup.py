import sys
import time

class Colours:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


INFO = "[{} INFO {}] ".format(Colours.OKBLUE, Colours.ENDC)
OK = "[{}  OK  {}] ".format(Colours.OKGREEN, Colours.ENDC)
WARN = "[{} WARN {}] ".format(Colours.WARNING, Colours.ENDC)
ERROR = "[{} ERROR {}] ".format(Colours.FAIL, Colours.ENDC)
INPUT = "[{} .... {}] ".format(Colours.OKBLUE, Colours.ENDC)


# Version Checking
# Basically reject anything not 3.5 or 3.6 as those are the only versions that work.

if sys.version_info < (3,5):
	print("{0} Roxbot does not support Python {1}.{2}. Roxbot only works on 3.5 - 3.7".format(ERROR, sys.version_info[0], sys.version_info[1]))
	exit(0)
else:
	import configparser


# Install Requirements
def requirements():
	print("{} Installing requirements".format(INFO))
	args = ["install", "-U", "-r", "requirements.txt"]
	if '-v' not in sys.argv:
		args.append("-q")
	try:
		import pip
		code = pip.main(args)
	except AttributeError:  # Has pip 10 installed
		from pip._internal import main
		code = main(args)
	except ImportError:
		print("{} Pip not installed. Please install pip before continuing.".format(ERROR))
		exit(1)

	if code != 0:
		print("{} Error occurred while installing requirements. Please use the option '-v' to get verbose output from pip".format(ERROR))
		print("{} Exiting...".format(ERROR))
		exit(1)
	else:
		print("{} Requirements successfully installed.".format(OK))


# Create preferences file.

def create_preferences_file():
	time.sleep(.5)
	print("{} Creating preferences.ini file...".format(INFO))
	with open("roxbot/settings/preferences_example.ini", "r") as orig:
		fp = orig.read()
		with open("roxbot/settings/preferences.ini", "w") as new:
			new.write(fp)
	time.sleep(.5)
	print("{} Preferences file created".format(OK))
	time.sleep(.5)


def preferences_setup():
	# Ask to do preferences.ini setup
	print("{} Most of the setup is complete. All there is to do is setup the preferences.ini file.".format(INFO))
	print("{} You can do the quick setup in this script, or manually setup the file yourself.".format(INFO))
	print("")
	while True:
		choice = input("{} Do you want to continue to the easy preferences setup? (y/n): ".format(INFO))
		if choice.strip(" ").lower() == "y":
			time.sleep(.5)
			print("")
			print("{} Everything asked for next is required. Please try and input every option. "
				  "If not possible, it is required you fix this in the preferences.ini file later.".format(WARN))
			print("")
			break
		elif choice.strip(" ").lower() == "n":
			print("{} Exiting...".format(OK))
			exit(0)

	# Preferences.ini setup

	config = configparser.ConfigParser()
	config.read("roxbot/settings/preferences.ini")
	print("{} Setting up preferences file...".format(INFO))

	# OWNER ID
	owner_id = str(input("{} Bot Owner ID: ".format(INPUT))).strip(" ")
	if not owner_id or not owner_id.isdigit():
		print("{} Invalid owner ID given. Skipping...".format(WARN))
	else:
		config["Roxbot"]["OwnerID"] = owner_id
		print("{} OWNER ID set to '{}'".format(OK, owner_id))
	print("")

	# COMMAND PREFIX
	prefix = str(input("{} Command Prefix: ".format(INPUT))).strip(" ")
	if not prefix:
		print("{} Invalid Command Prefix given. Skipping...".format(WARN))
	else:
		config["Roxbot"]["Command_Prefix"] = prefix
		print("{} COMMAND PREFIX set to '{}'".format(OK, prefix))
	print("")

	# BOT TOKEN
	token = str(input("{} Discord Bot Token: ".format(INPUT))).strip(" ")
	if not token:
		print("{} Invalid token given. Skipping...".format(WARN))
	else:
		config["Tokens"]["Discord"] = token
		print("{} DISCORD TOKEN set to '{}'".format(OK, token))
	print("")

	# IMGUR CLIENT ID
	token = str(input("{} Imgur Client ID: ".format(INPUT))).strip(" ")
	if not token:
		print("{} Invalid client ID given. Skipping...".format(WARN))
	else:
		config["Tokens"]["Imgur"] = token
		print("{} IMGUR ID set to '{}'".format(OK, token))
	print("")

	# SAVE
	# TODO: Add comments back in once preferences.ini has been rewritten
	print("{} Finished preferences.ini setup.".format(OK))
	with open("roxbot/settings/preferences.ini", 'w') as configfile:
		config.write(configfile)

	print("{} There are more options avaliable in the file (found at ./roxbot/settings/preferences.ini) if you want to make optional tweaks to Roxbot.".format(INFO))
	print("{} Exiting...".format(OK))
	exit(0)


def main():
	try:
		requirements()
		create_preferences_file()
		preferences_setup()
	except KeyboardInterrupt:
		print("")
		print("{} Install script ended via KeyboardInterrupt".format(ERROR))


if __name__ == "__main__":
	main()
