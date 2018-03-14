import datetime
import time
import checks
import discord
from config.server_config import ServerConfig
from discord.ext.commands import bot, group, guild_only, bot_has_permissions


class Admin():
	"""
	Admin Commands for those admins
	"""
	def __init__(self, Bot):
		self.bot = Bot
		self.slow_mode = False
		self.slow_mode_channels = {}
		self.users = {}
		self.con = ServerConfig()
		self.servers = self.con.servers

	async def on_message(self, message):
		# Slow Mode Code
		channel = message.channel
		author = message.author

		if not author == self.bot.user:
			if self.slow_mode and channel.id in self.slow_mode_channels:
				if author.id not in self.users[channel.id]:
					# If user hasn't sent a message in this channel after slow mode was turned on
					self.users[channel.id][author.id] = message.created_at
				else:
					# Else, check when their last message was and if time is smaller than the timer, delete the message.
					timer = datetime.timedelta(seconds=self.slow_mode_channels[channel.id])
					if message.timestamp - self.users[channel.id][author.id] < timer:
						await message.delete()
					else:
						self.users[message.channel.id][author.id] = message.created_at
			else:
				pass

	@guild_only()
	@checks.is_admin_or_mod()
	@bot_has_permissions(manage_messages=True)
	@bot.command()
	async def slowmode(self, ctx, time):
		"""Puts the current channel in slowmode.
		Usage:
			;slowmode [time/"off"]
			time = time of the cooldown between messages a user has.
			off = turns off slowmode for this channel"""
		if time == "off" and self.slow_mode: # Turn Slow Mode off
			self.slow_mode = False
			self.slow_mode_channels.pop(ctx.channel.id)
			self.users.pop(ctx.channel.id)
			return await ctx.send("Slowmode off")

		elif time.isdigit() and not self.slow_mode: # Turn Slow Mode On
			self.users[ctx.channel.id] = {}
			self.slow_mode_channels[ctx.channel.id] = int(time)
			self.slow_mode = True
			return await ctx.send("Slowmode on :snail: ({} seconds)".format(time))

		elif time.isdigit and self.slow_mode: # Change value of Slow Mode timer
			self.slow_mode_channels[ctx.channel.id] = int(time)
			return await ctx.send("Slowmode set to :snail: ({} seconds)".format(time))

		else:
			pass

	@checks.is_admin_or_mod()
	@group()
	async def warn(self, ctx):
		"""Group of commands handling warnings
		Options:
			add
			remove
			list"""
		if ctx.invoked_subcommand is None:
			return await ctx.send('Missing Argument')

	@warn.command()
	async def add(self, ctx, user: discord.User = None, *, warning = ""):
		# Warning in the config is a dictionary of user ids. The user ids are equal to a list of dictionaries.
		self.servers = self.con.load_config()
		warning_limit = 2
		id = str(ctx.guild.id)
		warning_dict = {
			"warned-by": ctx.author.id,
			"date": time.time(),
			"warning": warning
		}

		if not user.id in self.servers[id]["warnings"]:
			self.servers[id]["warnings"][user.id] = []
		self.servers[id]["warnings"][user.id].append(warning_dict)

		self.con.update_config(self.servers)

		amount_warnings = len(self.servers[id]["warnings"][user.id])
		if amount_warnings > warning_limit:
			await ctx.author.send("{} has been reported {} time(s). This is a reminder that this is over the set limit of {}.".format(
					str(user), amount_warnings, warning_limit))

		return await ctx.send("Reported {}.".format(user.name+"#"+user.discriminator))


	@warn.command()
	async def list(self, ctx, *, user: discord.User = None):
		if user == None:
			output = ""
			for member in self.servers[str(ctx.guild.id)]["warnings"]:
				# Remove users with no warning here instead of remove cause im lazy
				if not self.servers[str(ctx.guild.id)]["warnings"][member]:
					self.servers[str(ctx.guild.id)]["warnings"].pop(member)
				else:
					member_obj = discord.utils.get(ctx.guild.members, id=int(member))
					if member_obj:
						output += "{}: {} Warning(s)\n".format(str(member_obj), len(
							self.servers[str(ctx.guild.id)]["warnings"][member]))
					else:
						output += "{}: {} Warning(s)\n".format(member, len(
							self.servers[str(ctx.guild.id)]["warnings"][member]))
			return await ctx.send(output)

		if not self.servers[str(ctx.guild.id)]["warnings"][str(user.id)]:
			self.servers[str(ctx.guild.id)]["warnings"].pop(str(user.id))
		if not user.id in self.servers[str(ctx.guild.id)]["warnings"]:
			return await ctx.send("This user doesn't have any warning on record.")
		em = discord.Embed(title="Warnings for {}".format(str(user)), colour=0XDEADBF)
		em.set_thumbnail(url=user.avatar_url)
		x = 1
		userlist = self.servers[str(ctx.guild.id)]["warnings"][user.id]
		for warning in userlist:
			try:
				warned_by = str(await self.bot.get_user_info(warning["warned-by"]))
			except:
				warned_by = warning["warned-by"]
			date = datetime.datetime.fromtimestamp(warning["date"]).strftime('%c')
			warn_reason = warning["warning"]
			em.add_field(name="Warning %s"%x, value="Warned by: {}\nTime: {}\nReason: {}".format(warned_by, date, warn_reason))
			x += 1
		return await ctx.send(embed=em)

	@warn.command()
	async def remove(self, ctx, user: discord.User = None, index = None):
		self.servers = self.con.load_config()
		if index:
			try:
				index = int(index)
				index -= 1
				self.servers[str(ctx.guild.id)]["warnings"][user.id].pop(index)
				if not self.servers[str(ctx.guild.id)]["warnings"][user.id]:
					self.servers[str(ctx.guild.id)]["warnings"].pop(user.id)

				self.con.update_config(self.servers)
				return await ctx.send("Removed Warning {} from {}".format(index+1, str(user)))

			except Exception as e:
				if isinstance(e, IndexError):
					return await ctx.send(":warning: Index Error.")
				elif isinstance(e, KeyError):
					return await ctx.send("Could not find user in warning list.")
				elif isinstance(e, ValueError):
					return await ctx.send("Please enter a valid index number.")
				else:
					raise e
		else:
			try:
				self.servers[str(ctx.guild.id)]["warnings"].pop(user.id)
				self.con.update_config(self.servers)
				return await ctx.send("Removed all warnings for {}".format(str(user)))
			except KeyError:
				return await ctx.send("Could not find user in warning list.")


def setup(Bot):
	Bot.add_cog(Admin(Bot))
