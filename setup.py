import os
import sys
import configparser

# Version Checking
# Basically reject anything not 3.5 or 3.6 as those are the only versions that work.

if not (sys.version_info[:2] == (3, 5) or sys.version_info[:2] == (3, 6)):
	print("Roxbot does not support Python {}.{}".format(sys.version_info[0],sys.version_info[1]))
	exit(0)

# Install Requirements

code = os.system("python3 -m pip install -r requirements.txt")
if code != 0:
	print("Error occurred while installing requirements. Exiting...")
	exit(1)
else:
	print("Requirements successfully installed.")

# Create preferences file.

with open("roxbot/settings/preferences_example.ini", "r") as orig:
	fp = orig.read()
	with open("roxbot/settings/preferences.ini", "w") as new:
		new.write(fp)
		print("Preferences file created")

# Ask to do preferences.ini setup

print("Most of the setup is complete. All there is to do is setup the preferences.ini file.")
print("You can do the quick setup in this script, or manually setup the file yourself.")
while True:
	choice = input("Do you want to continue to the easy preferences setup? (y/n): ")
	if choice.strip(" ").lower() == "y":
		print("You can leave the field empty if you don't have the required thing.")
		print("Note: Everything that is asked here is required and not having it can lead ot issues.")
		break
	elif choice.strip(" ").lower() == "n":
		print("Exiting...")
		exit(0)

# Preferences.ini setup

config = configparser.ConfigParser()
config.read("roxbot/settings/preferences.ini")
print("Setting up preferences file...")

owner_id = str(input("Bot Owner ID: ")).strip(" ")
if not owner_id or not owner_id.isdigit():
	print("Invalid owner ID given. Skipping...")
else:
	config["Roxbot"]["OwnerID"] = owner_id

prefix = str(input("Command Prefix: ")).strip(" ")
if not prefix:
	print("Invalid Owner ID given. Skipping...")
else:
	config["Roxbot"]["Command_Prefix"] = prefix

token = str(input("Discord Bot Token: ")).strip(" ")
if not token:
	print("Invalid token given. Skipping...")
else:
	config["Tokens"]["Discord"] = token

token = str(input("Imgur Client ID: ")).strip(" ")
if not token:
	print("Invalid client ID given. Skipping...")
else:
	config["Tokens"]["Imgur"] = token

print("Finished preferences.ini setup.")
with open("roxbot/settings/preferences.ini", 'w') as configfile:
	config.write(configfile)

print("There are more options avaliable in the file (found at ./roxbot/settings/preferences.ini) if you want to make optional tweaks to Roxbot.")
print("Exiting...")
