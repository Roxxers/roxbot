import json
cogs = [
    'cogs.Admin',
    'cogs.Twitch',
    'cogs.selfAssign',
    'cogs.Fun'
]
with open('config/config.json', 'r') as config_file:
    serverconfig = json.load(config_file)
