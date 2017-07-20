import json


class Config():
    def __init__(self, bot):
        # TODO: Move default message into settings.ini
        self.serverconfig_template = {
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
                    }
                }
            }
        }
        self.serverconfig = self.load_config()
        self.bot = bot
        self.no_perms_reponse = ":no_entry_sign: You do not have permission to use this command."
        self.delete_after = 20

    async def on_server_join(self, server):
        self.serverconfig[server.id] = self.serverconfig_template["example"]
        self.updateconfig()

    async def on_server_remove(self, server):
        self.serverconfig.pop(server.id)
        self.updateconfig()

    def load_config(self):
        with open('config/config.json', 'r') as config_file:
            return json.load(config_file)

    def updateconfig(self):
        with open('config/config.json', 'w') as conf_file:
            json.dump(self.serverconfig, conf_file)

    def config_errorcheck(self):
        # TODO: Fix so that it checks for problems in children of module settings. i.e children of 'greets'
        # TODO: Fix issue where a setting can be enabled when it has no channel to post to.
        for server in self.bot.servers:
            if server.id not in self.serverconfig:
                self.serverconfig[server.id] = self.serverconfig_template["example"]
                self.updateconfig()
                print(
                    "WARNING: The config file for {} was not found. A template has been loaded and saved. All modules are turned off by default.".format(
                        server.name.upper()))
            else:
                for module_setting in self.serverconfig_template["example"]:
                    if module_setting not in self.serverconfig[server.id]:
                        self.serverconfig[server.id][module_setting] = self.serverconfig_template["example"][
                            module_setting]
                        self.updateconfig()
                        print(
                            "WARNING: The config file for {} was missing the {} module. This has been fixed with the template version. It is disabled by default.".format(
                                server.name.upper(), module_setting.upper()))
        print("")


def setup(bot):
    bot.add_cog(Config(bot))
