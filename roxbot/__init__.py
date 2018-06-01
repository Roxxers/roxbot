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


from roxbot import checks, http, guild_settings, converters, utils
from roxbot.enums import EmbedColours
from roxbot.logging import log
from roxbot.utils import blacklisted

import configparser


settings = configparser.ConfigParser()
settings.read("roxbot/settings/preferences.ini")

command_prefix = settings["Roxbot"]["Command_Prefix"]
owner = int(settings["Roxbot"]["OwnerID"])

token = settings["Tokens"]["Discord"]
tat_token = settings["Tokens"]["Tatsumaki"]
imgur_token = settings["Tokens"]["Imgur"]


__description__ = """RoxBot, A Discord Bot made by a filthy Mercy Main. Built with love (and discord.py) by Roxxers#7443.

[Github link](https://github.com/Roxxers/roxbot)
[Changelog](https://github.com/Roxxers/roxbot/wiki/Changelog)
[Found a bug or need to report an issue? Report it here](https://github.com/Roxxers/roxbot/issues/new)
[Say Thanks](https://saythanks.io/to/Roxxers)"""
__author__ = "Roxanne Gibson"
__version__ = "1.8.0a"
