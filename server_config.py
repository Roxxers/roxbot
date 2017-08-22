import json

class ServerConfig():
	def __init__(self):
		# TODO: Move default message into settings.ini
		self.servers_template = {
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
				"selfAssign": {
					"enabled": 0,
					"roles": []
				},
				"twitch": {
					"enabled": 0,
					"twitch-channel": "",
					"whitelist": {
						"enabled": 0,
						"list": []
					},
				},
				"mute": {
					"role": "",
					"admin-role": []
				}
			}
		}
		self.servers = self.load_config()
		# TODO: Move this to Checks
		self.no_perms_reponse = ":no_entry_sign: You do not have permission to use this command."
		self.delete_after = 20

	def load_config(self):
		with open('config/config.json', 'r') as config_file:
			return json.load(config_file)

	def update_config(self, config):
		with open('config/config.json', 'w') as conf_file:
			json.dump(config, conf_file)

	def errorcheck(self, servers):
		# TODO: Fix so that it checks for problems in children of module settings. i.e children of 'greets'
		# TODO: Fix issue where a setting can be enabled when it has no channel to post to.
		for server in servers:
			if server.id not in self.servers:
				self.servers[server.id] = self.servers_template["example"]
				self.update_config(self.servers)
				print(
					"WARNING: The config file for {} was not found. A template has been loaded and saved. All modules are turned off by default.".format(
						server.name.upper()))
			else:
				for module_setting in self.servers_template["example"]:
					if module_setting not in self.servers[server.id]:
						self.servers[server.id][module_setting] = self.servers_template["example"][
							module_setting]
						self.update_config(self.servers)
						print(
							"WARNING: The config file for {} was missing the {} module. This has been fixed with the template version. It is disabled by default.".format(
								server.name.upper(), module_setting.upper()))
		print("")