# Roxbot

[![Banner](http://i.imgur.com/SZIVXEg.png)](https://github.com/Roxxers)

[![Python](https://img.shields.io/badge/Python-3.5%2B-blue.svg?style=flat-square)](https://gitlab.roxxers.xyz/roxxers/roxbot)
[![MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square)](https://gitlab.roxxers.xyz/roxxers/roxbot/blob/master/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[<img src="https://discordapp.com/api/guilds/450805414024577035/widget.png?style=shield">](https://discord.gg/Mpz8nv7)

Roxbot: An inclusive modular multi-purpose Discord bot. Built with love (and discord.py) by Roxxers#7443.

Roxbot is designed to be provide many different services for users and moderators alike with a focus on customisability. Roxbot also has a focus on being inclusive and being fun for all kinds of people. Roxbot is a bot written by a queer woman with the lgbt community in mind. 


[Changelog](https://github.com/Roxxers/roxbot/blob/master/CHANGELOG.md) - [Docs](https://roxxers.github.io/roxbot/) - [Command Docs](https://roxxers.github.io/roxbot/commands/)


## Quick Setup

Roxbot has only been tested on Linux machines so far so these instructions are written for Linux users.

Requirements:

- Python 3.5 or higher
- Pip (to install dependencies)
- A Discord bot account ([How to make a bot account](https://discordpy.readthedocs.io/en/rewrite/discord.html#creating-a-bot-account))

Optional Requirements:

- Imgur API client ID (for Reddit cog. Create a application to gain access to the Imgur API [here](https://api.imgur.com/oauth2/addclient))
- ffmpeg (for Voice cog [music bot])
- libopus (for Voice cog [music bot])

If you don't meet the requirements for a cog, be sure to comment out that cog in the `roxbot/__init__.py` file. 

1. Clone Roxbot to your system

    ```bash
    $  git clone https://github.com/roxxers/roxbot.git
    $  cd roxbot/
    ```

2. Create a venv for Roxbot

    ```bash
    $  python3 -m venv ./env
    $  source env/bin/activate      # For bash and zsh users
    $  source env/bin/activate.fish # For fish users
    ```
3. Install Python dependencies

    ```bash
    $  python3 -m pip install -r requirements.txt
    ```

4. Edit Roxbot's config to add your bot accounts token (and Imgur api token if you plan to use the Reddit cog) to the config, and also edit some other config settings. Then rename it so that Roxbot will be able to read it.

    ```bash
    $  nano roxbot/settings/roxbot_example.conf
    $  mv roxbot/settings/roxbot_example.conf roxbot/settings/roxbot.conf
    ```
    
5. Run Roxbot and she should setup everything if you haven't run her before.

    ```bash
    $  ./roxbot.py
    ```
    
## Need Support?

If you want Roxbot support, a support Discord can be found by clicking the Discord banner at the top of the readme,

## Support Me <small>If you want/can</small>

[![KoFi](https://i.imgur.com/IE2Qg79.png)](https://ko-fi.com/roxxers)

