import json


def get(guilds):
	guild_list = []
	for guild in guilds:
		guild = GuildSettings(guild)
		guild_list.append(guild)
	return guild_list

def get_guild(guilds, wanted_guild):
	for guild in guilds:
		if guild.id == wanted_guild.id:
			return guild
	return None

class GuildSettings(object):

	__slots__ = ["settings", "id", "nsfw", "self_assign", "greets", "goodbyes", "twitch", "perm_roles", "custom_commands", "warnings", "is_anal", "gss", "guild_template"]

	def __init__(self, guild):
		self.id = guild.id
		self.guild_template = {
			"example": {
				"greets": {
					"enabled": 0,
					"welcome-channel": "",
					"member-role": "",
					"custom-message": "",
					"default-message": "Be sure to read the rules."
				},
				"goodbyes": {
					"enabled": 0,
					"goodbye-channel": "",
				},
				"self_assign": {
					"enabled": 0,
					"roles": []
				},
				"twitch": {
					"enabled": 0,
					"channel": "",
					"whitelist": {
						"enabled": 0,
						"list": []
					}
				},
				"nsfw": {
					"enabled": 0,
					"channels": [],
					"blacklist": []
				},
				"perm_roles": {
					"admin": [],
					"mod": []
				},
				"custom_commands": {
					"0": {},
					"1": {}
				},
				"gss": {
					"log_channel": "",
					"required_days": "",
					"required_score": "",
				},
				"warnings": {},
				"is_anal": {"y/n": 0}
			}
		}
		self.get_settings()

	def _write_changes(self, config):
		with open('settings/servers.json', 'w') as conf_file:
			json.dump(config, conf_file)

	def _error_check(self):
		for server in self.settings:
			print(server)
			# Server ID needs to be made a string for this statement because keys have to be strings in JSON. Which is annoying now we use int for ids.
			server_id = str(server.id)
			if str(server_id) not in self.settings:
				self.settings[server_id] = self.guild_template["example"]
				self.update_settings(self.settings)
				print(
					"WARNING: The settings file for {} was not found. A template has been loaded and saved. All cogs are turned off by default.".format(
						server.name.upper()))
			else:
				for cog_setting in self.guild_template["example"]:
					if cog_setting not in self.settings[server_id]:
						self.settings[server_id][cog_setting] = self.guild_template["example"][
							cog_setting]
						self.update_settings(self.settings)
						print(
							"WARNING: The settings file for {} was missing the {} cog. This has been fixed with the template version. It is disabled by default.".format(
								server.name.upper(), cog_setting.upper()))
					for setting in self.guild_template["example"][cog_setting]:
						if setting not in self.settings[server_id][cog_setting]:
							self.settings[server_id][cog_setting][setting] = self.guild_template["example"][
								cog_setting][setting]
							self.update_settings(self.settings)
							print(
								"WARNING: The settings file for {} was missing the {} setting in the {} cog. This has been fixed with the template version. It is disabled by default.".format(
									server.name.upper(), setting.upper(), cog_setting.upper()))

		print("")

	def get_settings(self):
		with open('Roxbot/settings/servers.json', 'r') as config_file:
			self.settings = json.load(config_file)
		print(self.settings)
		print(type(self.settings))
		self._error_check()
		self.nsfw = self.settings[str(self.id)]["nsfw"]
		self.self_assign = self.settings[str(self.id)]["self_assign"]
		self.greets = self.settings[str(self.id)]["greets"]
		self.goodbyes = self.settings[str(self.id)]["goodbyes"]
		self.twitch = self.settings[str(self.id)]["twitch"]
		self.perm_roles = self.settings[str(self.id)]["perm_roles"]
		self.custom_commands = self.settings[str(self.id)]["custom_commands"]
		self.warnings = self.settings[str(self.id)]["warnings"]
		self.is_anal = self.settings[str(self.id)]["is_anal"]
		# Add custom cog settings loading here
		self.gss = self.settings[str(self.id)]["gss"]

	def update_settings(self, changed_dict, setting = None):
		self.get_settings()
		if setting:
			self.settings[str(self.id)][setting] = changed_dict
		else:
			self.settings[str(self.id)] = changed_dict
		self._write_changes(self.settings)
