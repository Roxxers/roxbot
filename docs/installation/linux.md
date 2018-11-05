---
title: Linux Installation
description: Guide to installing Roxbot on Linux.
authors:
    - Roxanne Gibson
---


# Linux Installation

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
