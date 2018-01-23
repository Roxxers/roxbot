import json

class ServerConfig():
	def __init__(self):
		# Admin role is how it is because of how I print out settings. Touch it and it will break that command.
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
				"self_assign": {
					"enabled": 0,
					"roles": []
				},
				"twitch": {
					"enabled": 0,
					"twitch-channel": "",
					"whitelist": {
						"enabled": 0,
						"list": []
					}
				},
				"nsfw": {
					"enabled": 0,
					"channels": []
				},
				"perm_roles": {
					"admin": [],
					"mod":[]
				},
				"custom_commands":{
					"0": {},
					"1": {}
				},
				"gss":{
					"log_channel": "",
					"required_days": "",
					"required_score": "",
				}
			}
		}
		self.servers = self.load_config()
		self.delete_after = 20

	def load_config(self):
		with open('config/servers.json', 'r') as config_file:
			return json.load(config_file)

	def update_config(self, config):
		with open('config/servers.json', 'w') as conf_file:
			json.dump(config, conf_file)

	def error_check(self, servers):
		for server in servers:
			if server.id not in self.servers:
				self.servers[server.id] = self.servers_template["example"]
				self.update_config(self.servers)
				print(
					"WARNING: The config file for {} was not found. A template has been loaded and saved. All cogs are turned off by default.".format(
						server.name.upper()))
			else:
				for cog_setting in self.servers_template["example"]:
					if cog_setting not in self.servers[server.id]:
						self.servers[server.id][cog_setting] = self.servers_template["example"][
							cog_setting]
						self.update_config(self.servers)
						print(
							"WARNING: The config file for {} was missing the {} cog. This has been fixed with the template version. It is disabled by default.".format(
								server.name.upper(), cog_setting.upper()))
					for setting in self.servers_template["example"][cog_setting]:
						if setting not in self.servers[server.id][cog_setting]:
							self.servers[server.id][cog_setting][setting] = self.servers_template["example"][
								cog_setting][setting]
							self.update_config(self.servers)
							print(
								"WARNING: The config file for {} was missing the {} setting in the {} cog. This has been fixed with the template version. It is disabled by default.".format(
									server.name.upper(), setting.upper(), cog_setting.upper()))

		print("")