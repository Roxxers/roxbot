#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017-2018 Roxanne Gibson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
import hashlib
import datetime
from roxbot.db import *

from roxbot.cogs.customcommands import CCCommands


@db_session
def admin_convert(guild_id, settings):
	warning_limit = settings.get("warning_limit", None)
	if warning_limit is not None:
		db.execute("UPDATE AdminSingle SET `warning_limit` = {} WHERE `guild_id` = {}".format(warning_limit, guild_id))
	db.commit()
	warnings = settings.get("warnings", None)
	if warnings is None:
		return
	for user, warns in warnings.items():
		user_id = int(user)
		for warn in warns:
			date = datetime.datetime.fromtimestamp(warn["date"])
			try:
				db.insert("AdminWarnings", user_id=user_id, guild_id=guild_id, date=date, warning=warn["warning"], warned_by=warn["warned-by"])
				db.commit()
			except (TransactionIntegrityError, IntegrityError):
				pass


@db_session
def custom_commands_convert(guild_id, settings):
	for com_type, commands in settings.items():
		if com_type != "convert":
			for name, command in commands.items():
				com_hash = hashlib.md5(name.encode() + str(guild_id).encode() + str(com_type).encode()).hexdigest()
				if isinstance(command, str):
					com = [command]
				else:
					com = command
				try:
					CCCommands(name=name, hash=com_hash, output=com, type=int(com_type), guild_id=guild_id)
					db.commit()
				except (TransactionIntegrityError, CacheIndexError, IntegrityError):
					pass

@db_session
def joinleave_convert(guild_id, settings):
	greet = settings["greets"]
	goodbye = settings["goodbyes"]
	db.execute("UPDATE `JoinLeaveSingle` SET `greets_enabled` = {} WHERE `guild_id` = {}".format(greet["enabled"], guild_id))
	db.execute("UPDATE `JoinLeaveSingle` SET `goodbyes_enabled` = {} WHERE `guild_id` = {}".format(goodbye["enabled"], guild_id))
	db.execute("UPDATE `JoinLeaveSingle` SET `greets_channel_id` = {} WHERE `guild_id` = {}".format(greet["welcome-channel"], guild_id))
	db.execute("UPDATE `JoinLeaveSingle` SET `goodbyes_channel_id` = {} WHERE `guild_id` = {}".format(goodbye["goodbye-channel"], guild_id))
	db.execute("UPDATE `JoinLeaveSingle` SET `greets_custom_message` = '{}' WHERE `guild_id` = {}".format(greet["custom-message"],guild_id))


@db_session
def nsfw_convert(guild_id, settings):
	db.execute("UPDATE `NSFWSingle` SET `enabled` = {} WHERE `guild_id` = {}".format(settings["enabled"], guild_id))
	db.execute('UPDATE `NSFWSingle` SET `blacklisted_tags` = "{}" WHERE `guild_id` = {}'.format(settings["blacklist"], guild_id))


@db_session
def logging_convert(guild_id, settings):
	db.execute("UPDATE `LoggingSingle` SET `enabled` = {} WHERE `guild_id` = {}".format(settings["enabled"], guild_id))
	db.execute('UPDATE `LoggingSingle` SET `logging_channel_id` = "{}" WHERE `guild_id` = {}'.format(settings["channel"], guild_id))


@db_session
def voice_convert(guild_id, settings):
	db.execute("UPDATE `VoiceSingle` SET `need_perms` = {} WHERE `guild_id` = {}".format(settings["need_perms"], guild_id))
	db.execute("UPDATE `VoiceSingle` SET `skip_voting` = {} WHERE `guild_id` = {}".format(settings["skip_voting"], guild_id))
	db.execute("UPDATE `VoiceSingle` SET `skip_ratio` = {} WHERE `guild_id` = {}".format(settings["skip_ratio"], guild_id))
	db.execute("UPDATE `VoiceSingle` SET `max_length` = {} WHERE `guild_id` = {}".format(settings["max_length"], guild_id))


@db_session
def selfassign_convert(guild_id, settings):
	db.execute("UPDATE `SelfAssignSingle` SET `enabled` = {} WHERE `guild_id` = {}".format(settings["enabled"], guild_id))
	for role in settings["roles"]:
		try:
			db.insert("SelfAssignRoles", role_id=role, guild_id=guild_id)
		except IntegrityError:
			pass


def check_convert(guilds):
	if os.path.isdir(os.getcwd() + "/roxbot/settings/servers"):
		for guild in guilds:
			settings = {}
			for cog in ("Admin.json", "Core.json", "CustomCommands.json", "JoinLeave.json", "NFSW.json", "SelfAssign.json", "Voice.json"):
				with open('roxbot/settings/servers/{}/{}'.format(guild.id, cog), 'r') as config_file:
					settings = {**settings, **json.load(config_file)}

			admin_convert(guild.id, settings["admin"])
			custom_commands_convert(guild.id, settings["custom_commands"])
			joinleave = {}
			joinleave["greets"] = settings["greets"]
			joinleave["goodbyes"] = settings["goodbyes"]
			joinleave_convert(guild.id, joinleave)
			nsfw_convert(guild.id, settings["nsfw"])
			logging_convert(guild.id, settings["logging"])
			voice_convert(guild.id, settings["voice"])
			selfassign_convert(guild.id, settings["self_assign"])
		os.rename(os.getcwd() + "/roxbot/settings/servers", os.getcwd() + "/roxbot/settings/servers.old")