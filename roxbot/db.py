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

import sqlite3
from os import getcwd
from pony.orm import *


db_dir = getcwd() + "/roxbot/settings/db.sqlite"
db = Database()
db.bind("sqlite", db_dir, create_db=True)


# Entities are committed to the db in the main file during boot up

async def populate_db(bot):
	db.generate_mapping(create_tables=True)
	await bot.wait_for("ready")
	populate_single_settings(bot)


def populate_single_settings(bot):
	for guild in bot.guilds:
		for name, cog in bot.cogs.items():
			try:
				if cog.autogen_db:
					with db_session:
						cog.autogen_db(guild_id=guild.id)
			except (AttributeError, TransactionIntegrityError):
				pass  # No DB settings or already in place


def delete_single_settings(guild):
	database = sqlite3.connect(db_dir)
	cursor = database.cursor()
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	for t in cursor.fetchall():
		table = t[0]
		try:
			cursor.execute("DELETE FROM {} WHERE guild_id={}".format(table, guild.id))
		except sqlite3.OperationalError:
			pass  # Table doesn't store guild_id
	database.commit()
	database.close()
