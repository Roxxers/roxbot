# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017-2018 Roxanne Gibson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import os
import json
import errno
import shutil


def _open_config(server, cogs):
	"""Opens the guild settings file

	servers: server id str
	cogs: list of cog names

	Returns
	=======
	servers.json: dict
	"""
	settings = {}
	for cog in cogs:
		with open('roxbot/settings/servers/{}/{}'.format(server, cog), 'r') as config_file:
			settings = {**settings, **json.load(config_file)}
	return settings


def _write_changes(guild_id, cogs, config):
	"""

	:param guild_id:
	:param cogs:
	:param config:
	:return:
	"""
	for cog in cogs:
		with open('roxbot/settings/servers/{}/{}'.format(guild_id, cog), "r") as conf_file:
			file = json.load(conf_file)
		with open('roxbot/settings/servers/{}/{}'.format(guild_id, cog), "w") as conf_file:
			for key in config.keys():
				if key in file.keys():
					file[key] = config[key]
			json.dump(file, conf_file)


def backup(name):
	try:
		shutil.copytree('roxbot/settings/servers', 'roxbot/settings/backups/{}'.format(name))
	except OSError as e:
		# If the error was caused because the source wasn't a directory
		if e.errno == errno.ENOTDIR:
			shutil.copy('roxbot/settings/servers', 'roxbot/settings/backups/{}'.format(name))
		else:
			print('Directory not copied. Error: %s' % e)


def remove_guild(guild):
	"""Removes given guild from settings folders and saves changes."""
	shutil.rmtree('roxbot/settings/server/{}'.format(guild.id))


def add_guild(guild, cogs):
	"""Adds given guild to settings folder saves changes."""
	_make_server_folder(guild, cogs)


def _make_cog_json_file(server_id, name, data):
	with open("roxbot/settings/servers/{}/{}.json".format(server_id, name), "w") as fp:
		return json.dump(data, fp)

def _check_for_missing_cog(server_id, name, cog):
	try:
		if cog.settings and (cog.settings.get("limited_to_guild", server_id) == server_id):
			try:
				cog.settings.pop("limited_to_guild")
			except KeyError:
				pass  # limited_to_guild is a arg that can be passed to limit a cog to one server.
			print("{}.json".format(name))
			if "{}.json".format(name) not in os.listdir("roxbot/settings/servers/{}".format(server_id)):
				_make_cog_json_file(server_id, name, cog.settings)
				return True
	except AttributeError:
		pass  # If Cog has no settings
	return False


def _make_server_folder(server, cogs):
	os.mkdir("roxbot/settings/servers/{}".format(str(server.id)))
	for name, cog in cogs.items():
		_check_for_missing_cog(str(server.id), name, cog)


def error_check(servers, cogs):
	# Check for missing servers folder
	if "servers" not in os.listdir("roxbot/settings/"):
		print("WARNING: Settings folder not found, making new default settings folder.")
		os.mkdir("roxbot/settings/servers")
		for server in servers:
			_make_server_folder(server, cogs)

	else:
		for server in servers:
			# Server ID made a string for ease of use
			server_id = str(server.id)

			# Check for missing server
			if server_id not in os.listdir("roxbot/settings/servers/"):
				_make_server_folder(server, cogs)
				print("WARNING: The settings folder for {} was not found. The defaults have been created.".format(str(server)))

			# Check for missing cog settings
			for name, cog in cogs.items():
				resp = _check_for_missing_cog(server_id, name, cog)
				if resp:
					print("WARNING: The settings folder for {} is missing the file {}. The defaults have been created.".format(str(server), name))


def get(guild):
	"""
	Gets a single GuildSettings Object representing the settings of that guild
	:param guild: :type discord.Guild:
	:return Single GuildSettings Object: :type GuildSettings:
	"""
	return GuildSettings(guild)


class GuildSettings(object):
	"""
	An Object to store all settings for one guild.
	The goal is to make editing settings a lot easier and make it so you don't have to handle things like ID's which caused a lot of issues when moving over to discord.py 1.0
	"""
	__slots__ = ["settings", "id", "name", "cogs"]

	def __init__(self, guild):
		self.id = guild.id
		self.name = str(guild)
		self.cogs = os.listdir("roxbot/settings/servers/{}".format(self.id))
		self.settings = self.refresh()

	def __str__(self):
		return self.name

	def __iter__(self):
		list_settings = list(self.settings)
		list_settings.sort()
		for setting in list_settings:
			yield setting

	def __getitem__(self, key):
		return self.settings[key]

	@staticmethod
	def _convert(settings, option="int"):
		"""
		Converts values between int and str in the settings dict/json. Required due to how ID's are ints in discord.py
		and we can't store int's that big in a json file.
		:param settings:
		:param option:
		:return:
		"""
		for key, setting in settings.items():
			if setting.get("convert"):
				for x in setting["convert"].keys():
					if setting["convert"][x] not in ("bool", "hide"):
						if isinstance(setting[x], list):
							for y, value in enumerate(setting[x]):
								if option == "str":
									setting[x][y] = str(value)
								else:
									setting[x][y] = int(value)
						else:
							if option == "str":
								setting[x] = str(setting[x])
							else:
								setting[x] = int(setting[x])
			settings[key] = setting
		return settings

	def refresh(self):
		"""
		Open the settings, convert them to a usable format, and return for roxbot usage.
		:return:
		"""
		settings = _open_config(self.id, self.cogs)
		self._convert(settings)
		return settings

	def update(self, changed_dict, setting = None):
		"""
		Get latest settings, and update them with a change.
		:param changed_dict:
		:param setting: Setting should be a str of the setting key.
		If nothing is passed, it is assumed changed_dict is the settings file for the whole server.
		THIS IS NOT RECOMMENED. Always try and just pass the cogs settings and not a whole settings file.
		:return:
		"""
		self.settings = self.refresh()
		settings = self.settings.copy()
		if setting is not None:
			settings[setting] = changed_dict
		elif isinstance(changed_dict, dict):
			settings = changed_dict
		elif isinstance(changed_dict, GuildSettings):
			settings = changed_dict.settings
		else:
			raise TypeError("changed_dict can only be a dict or GuildSettings object.")
		settings = self._convert(settings, "str")
		_write_changes(self.id, self.cogs, settings)
