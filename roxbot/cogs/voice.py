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


import os
import asyncio
import discord
import datetime
import youtube_dl
from math import ceil
from discord.ext import commands

import roxbot
from roxbot import guild_settings


def _clear_cache():
	"""Clears the cache folder for the music bot. Ignores the ".gitignore" file to avoid deleting versioned files."""
	for file in os.listdir("roxbot/cache"):
		if file != ".gitignore":
			os.remove("roxbot/cache/{}".format(file))


def _format_duration(duration):
	"""Static method to turn the duration of a file (in seconds) into something presentable for the user"""
	if not duration:
		return duration
	hours = duration // 3600
	minutes = (duration % 3600) // 60
	seconds = duration % 60
	format_me = {"second": int(seconds), "minute": int(minutes), "hour": int(hours)}
	formatted = datetime.time(**format_me)
	output = "{:%M:%S}".format(formatted)
	if formatted.hour >= 1:
		output = "{:%H:}".format(formatted) + output
	return output


def volume_perms():
	def predicate(ctx):
		gs = guild_settings.get(ctx.guild)
		if gs.voice["need_perms"]:  # Had to copy the admin or mod code cause it wouldn't work ;-;
			if ctx.message.author.id == roxbot.owner:
				return True
			else:
				admin_roles = gs.perm_roles["admin"]
				mod_roles = gs.perm_roles["mod"]
				for role in ctx.author.roles:
					if role.id in mod_roles or role.id in admin_roles:
						return True
			return False
		else:
			return True
	return commands.check(predicate)


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': './roxbot/cache/%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
}

ffmpeg_options = {
	'before_options': '-nostdin',
	'options': '-vn -loglevel panic'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class ModifiedFFmpegPMCAudio(discord.FFmpegPCMAudio):
	"""Modifies the read function of FFmpegPCMAudio to add a timer.
	Thanks to eliza(nearlynon#3292) for teaching me how to do this"""
	def __init__(self, source, options):
		super().__init__(source, **options)
		self.timer = 0

	def read(self):
		self.timer += 20
		return super().read()


class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume):
		self.source = source
		super().__init__(self.source, volume)
		self.data = data
		self.title = data.get('title')
		self.uploader = data.get("uploader")
		self.uploader_url = data.get("uploader_url")
		self.url = data.get('url')
		self.duration = data.get("duration")
		self.host = data.get("extractor_key")
		self.webpage_url = data.get('webpage_url')
		self.thumbnail_url = data.get("thumbnail", "")

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False, volume=0.2):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
			# take first item from a playlist. This shouldn't need to happen but in case it does.
			data = data['entries'][0]

		filename = data['url'] if stream else ytdl.prepare_filename(data)
		return cls(ModifiedFFmpegPMCAudio(filename, ffmpeg_options), data=data, volume=volume)


class Voice:
	def __init__(self, bot):
		# Auto Cleanup cache files on boot
		_clear_cache()

		# Setup variables and then add dictionary entries for all guilds the bot can see on boot-up.
		self.bot = bot
		self.refresh_rate = 1/60  # 60hz
		self._volume = {}
		self.playlist = {}  # All audio to be played
		self.skip_votes = {}
		self.am_queuing = {}
		self.now_playing = {}  # Currently playing audio
		self.queue_logic = {}
		for guild in bot.guilds:
			self._volume[guild.id] = 0.2
			self.playlist[guild.id] = []
			self.skip_votes[guild.id] = []
			self.am_queuing[guild.id] = False
			self.now_playing[guild.id] = None
			self.queue_logic[guild.id] = None

	async def on_guild_join(self, guild):
		"""Makes sure that when the bot joins a guild it won't need to reboot for the music bot to work."""
		self.playlist[guild.id] = []
		self.skip_votes[guild.id] = []
		self.am_queuing[guild.id] = False
		self.now_playing[guild.id] = None
		self.queue_logic[guild.id] = None

	async def _queue_logic(self, ctx):
		"""Background task designed to help the bot move on to the next video in the queue"""
		try:
			while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
				await asyncio.sleep(self.refresh_rate)
		except AttributeError:
			pass  # This is to stop any errors appearing if the bot suddenly leaves voice chat.
		self.now_playing[ctx.guild.id] = None
		self.skip_votes[ctx.guild.id] = []
		if self.playlist[ctx.guild.id] and ctx.voice_client:
			player = self.playlist[ctx.guild.id].pop(0)
			await ctx.invoke(self.play, url=player, stream=player.get("stream", False), from_queue=True, queued_by=player.get("queued_by", None))

	def _queue_song(self, ctx, video, stream):
		"""Fuction to queue up a video into the playlist."""
		video["stream"] = stream
		video["queued_by"] = ctx.author
		self.playlist[ctx.guild.id].append(video)
		return video

	def _generate_np_embed(self, guild, playing_status):
		np = self.now_playing[guild.id]
		title = "{0}: '{1.title}' from {1.host}".format(playing_status, np)
		duration = _format_duration(np.duration)
		time_played = _format_duration(np.source.timer/1000)

		embed = discord.Embed(title=title, colour=roxbot.EmbedColours.pink, url=np.webpage_url)
		embed.description = "Uploaded by: [{0.uploader}]({0.uploader_url})\nURL: [Here]({0.webpage_url})\nDuration: {1}\nQueued by: {0.queued_by}".format(np, duration)
		if np.thumbnail_url:
			embed.set_image(url=np.thumbnail_url)
		embed.set_footer(text="{}/{} | Volume: {}%".format(time_played, duration, int(self.now_playing[guild.id].volume*100)))
		return embed

	@roxbot.checks.is_admin_or_mod()
	@commands.command()
	async def join(self, ctx, *, channel: discord.VoiceChannel = None):
		"""Joins the voice channel your in."""
		# Get channel
		if channel is None:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				raise commands.CommandError("Failed to join voice channel. Please specify a channel or join one for Roxbot to join.")

		# Join VoiceChannel
		if ctx.voice_client is not None:
			await ctx.voice_client.move_to(channel)
		else:
			await channel.connect()
		return await ctx.send("Joined {0.name} :ok_hand:".format(channel))

	@commands.cooldown(1, 0.5, commands.BucketType.guild)
	@commands.command(aliases=["yt"])
	async def play(self, ctx, *, url, stream=False, from_queue=False, queued_by=None):
		"""Plays from a url or search query (almost anything youtube_dl supports)"""
		voice = guild_settings.get(ctx.guild).voice
		guild = ctx.guild

		# Checks if invoker is in voice with the bot. Skips admins and mods and owner and if the song was queued previously.
		if not (roxbot.checks._is_admin_or_mod(ctx) or from_queue):
			if not ctx.author.voice:
				raise commands.CommandError("You're not in the same voice channel as Roxbot.")
			if ctx.author.voice.channel != ctx.voice_client.channel:
				raise commands.CommandError("You're not in the same voice channel as Roxbot.")

		# For internal speed. This should make the playlist management quicker when play is being invoked internally.
		if isinstance(url, dict):
			video = url
			url = video.get("webpage_url")
		else:
			video = ytdl.extract_info(url, download=False)

		# Playlist and search handling.
		if 'entries' in video and video.get("extractor_key") != "YoutubeSearch":
			await ctx.send("Looks like you have given me a playlist. I will queue up all {} videos in the playlist.".format(len(video.get("entries"))))
			data = dict(video)
			video = data["entries"].pop(0)
			for entry in data["entries"]:
				self._queue_song(ctx, entry, stream)
		elif 'entries' in video and video.get("extractor_key") == "YoutubeSearch":
			video = video["entries"][0]

		# Duration limiter handling
		if video.get("duration", 1) > voice["max_length"] and not roxbot.checks._is_admin_or_mod(ctx):
			raise commands.CommandError("Cannot play video, duration is bigger than the max duration allowed.")

		# Actual playing stuff section.
		# If not playing and not queuing, and not paused, play the song. Otherwise queue it.
		if (not ctx.voice_client.is_playing() and self.am_queuing[guild.id] is False) and not ctx.voice_client.is_paused():
			self.am_queuing[guild.id] = True

			async with ctx.typing():
				player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=stream, volume=self._volume[ctx.guild.id])
				player.stream = stream
				player.queued_by = queued_by or ctx.author
				self.now_playing[guild.id] = player
				self.am_queuing[guild.id] = False

				ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

			# Create task to deal with what to do when the video ends or is skipped and how to handle the queue
			self.queue_logic[ctx.guild.id] = self.bot.loop.create_task(self._queue_logic(ctx))

			embed = self._generate_np_embed(ctx.guild, "Now Playing")
			await ctx.send(embed=embed)
		else:
			# Queue the song as there is already a song playing or paused.
			self._queue_song(ctx, video, stream)

			# Sleep because if not, queued up things will send first and probably freak out users or something
			while self.am_queuing[guild.id] is True:
				await asyncio.sleep(self.refresh_rate)
			embed = discord.Embed(description='Added "{}" to queue'.format(video.get("title")), colour=roxbot.EmbedColours.pink)
			await ctx.send(embed=embed)

	@commands.cooldown(1, 0.5, commands.BucketType.guild)
	@commands.command()
	async def stream(self, ctx, *, url):
		"""Streams given link. Good for Twitch. (same as play, but doesn't predownload)"""
		# Just invoke the play command with the stream argument as true. Deals with everything else anyway.
		return await ctx.invoke(self.play, url=url, stream=True)

	@play.before_invoke
	@stream.before_invoke
	async def ensure_voice(self, ctx):
		"""Ensures the bot is in a voice channel before continuing and if it cannot auto join, raise an error."""
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				raise commands.CommandError("Roxbot is not connected to a voice channel and couldn't auto-join a voice channel.")

	@volume_perms()
	@commands.command()
	async def volume(self, ctx, volume):
		"""Changes the player's volume. Only accepts integers representing x% between 0-100% or "show", which will show the current volume."""
		if ctx.voice_client is None:
			raise commands.CommandError("Roxbot is not in a voice channel.")

		try:
			volume = int(volume)
		except ValueError:
			pass

		if volume != "show" and not isinstance(volume, int):
			raise commands.BadArgument("Not int or 'show'")
		elif volume == "show":
			return await ctx.send("Volume: {}%".format(self._volume[ctx.guild.id]*100))

		if 0 < volume <= 100:
			ctx.voice_client.source.volume = volume / 100  # Volume needs to be a float between 0 and 1... kinda
			self._volume[ctx.guild.id] = volume / 100  # Volume needs to be a float between 0 and 1... kinda
		else:
			raise commands.CommandError("Volume needs to be between 0-100%")
		return await ctx.send("Changed volume to {}%".format(volume))

	@commands.command()
	async def pause(self, ctx):
		"""Pauses the current video, if playing."""
		if ctx.voice_client is None:
			raise commands.CommandError("Roxbot is not in a voice channel.")
		else:
			if not ctx.voice_client.is_playing():
				return await ctx.send("Nothing is playing.")
			elif ctx.voice_client.is_paused():
				return await ctx.send("I already am paused!")
			else:
				ctx.voice_client.pause()
				return await ctx.send("Paused '{}'".format(ctx.voice_client.source.title))

	@commands.command()
	async def resume(self, ctx):
		"""Resumes the bot if paused. Also will play the next thing in the queue if the bot is stuck."""
		if ctx.voice_client is None:
			if len(self.playlist[ctx.guild.id]) < 1:
				raise commands.CommandError("Roxbot is not in a voice channel.")
			else:
				video = self.playlist[ctx.guild.id].pop(0)
				await ctx.invoke(self.play, url=video)
		else:
			if ctx.voice_client.is_paused():
				ctx.voice_client.resume()
				return await ctx.send("Resumed '{}'".format(ctx.voice_client.source.title))
			else:
				if ctx.voice_client.is_playing():
					return await ctx.send("Can't resume if I'm already playing something!")
				else:
					return await ctx.send("Nothing to resume.")

	@commands.command()
	async def skip(self, ctx, option=""):
		"""Skips or votes to skip the current video. Use option "--force" if your an admin and """
		voice = guild_settings.get(ctx.guild).voice
		if ctx.voice_client.is_playing():
			if voice["skip_voting"] and not (option == "--force" and roxbot.checks._is_admin_or_mod(ctx)):  # Admin force skipping
				if ctx.author in self.skip_votes[ctx.guild.id]:
					return await ctx.send("You have already voted to skip the current track.")
				else:
					self.skip_votes[ctx.guild.id].append(ctx.author)
					# -1 due to the bot being counted in the members generator
					ratio = len(self.skip_votes[ctx.guild.id]) / (len(ctx.voice_client.channel.members) - 1)
					needed_users = ceil((len(ctx.voice_client.channel.members) - 1) * voice["skip_ratio"])
					if ratio >= voice["skip_ratio"]:
						await ctx.send("{} voted the skip the video.".format(ctx.author))
						await ctx.send("Votes to skip now playing has been met. Skipping video...")
						self.skip_votes[ctx.guild.id] = []
					else:
						await ctx.send("{} voted the skip the song.".format(ctx.author))
						return await ctx.send("{}/{} votes required to skip the video. To vote, use the command `{}skip`".format(len(self.skip_votes[ctx.guild.id]), needed_users, ctx.prefix))
			else:
				await ctx.send("Skipped video")

			# This should be fine as the queue_logic function should handle moving to the next song and all that.
			self.now_playing[ctx.guild.id] = None
			ctx.voice_client.stop()
		else:
			await ctx.send("I'm not playing anything.")

	@commands.command(aliases=["np"])
	async def nowplaying(self, ctx):
		"""Displays the video now playing."""
		if self.now_playing[ctx.guild.id] is None:
			return await ctx.send("Nothing is playing.")
		else:
			if ctx.voice_client.is_paused():
				x = "Paused"
			else:
				x = "Now Playing"
			embed = self._generate_np_embed(ctx.guild, x)
			return await ctx.send(embed=embed)

	@commands.command()
	async def queue(self, ctx):
		"""Displays what videos are queued up and waiting to be played."""
		output = ""
		index = 1
		for video in self.playlist[ctx.guild.id]:
			output += "{}) '{}' queued by {}\n".format(index, video["title"], video["queued_by"])
			index += 1
		if output == "":
			output = "Nothing is up next. Maybe you should add something!"
		embed = discord.Embed(title="Queue", description=output, colour=roxbot.EmbedColours.pink)
		return await ctx.send(embed=embed)

	@roxbot.checks.is_admin_or_mod()
	@commands.command()
	async def remove(self, ctx, index):
		"""Removes a item from the queue with the given index. Can also input all to delete all queued items."""
		# Try and convert index into an into. If not possible, just move forward
		try:
			index = int(index)
		except ValueError:
			pass

		# If not str "all" or an int, raise error.
		if index != "all" and not isinstance(index, int):
			raise commands.CommandError("No valid option given.")
		elif index == "all":
			# Remove all queued items
			length = len(self.playlist[ctx.guild.id])
			self.playlist[ctx.guild.id] = []
			return await ctx.send("Removed all queued videos. ({})".format(length))
		else:
			try:
				# Try and remove item using index.
				removed = self.playlist[ctx.guild.id].pop(index-1)  # -1 because queue index shown starts from 1, not 0
				return await ctx.send("Removed '{}' from the queue.".format(removed.get("title", index)))
			except IndexError:
				raise commands.CommandError("Valid Index not given.")

	@roxbot.checks.is_admin_or_mod()
	@commands.command(alaises=["disconnect"])
	async def stop(self, ctx):
		"""Stops and disconnects the bot from voice."""
		if ctx.voice_client is None:
			raise commands.CommandError("Roxbot is not in a voice channel.")
		else:
			# Clear up variables before stopping.
			self.playlist[ctx.guild.id] = []
			self.now_playing[ctx.guild.id] = None
			self.queue_logic[ctx.guild.id].cancel()
			await ctx.voice_client.disconnect()
			return await ctx.send(":wave:")


def setup(bot_client):
	bot_client.add_cog(Voice(bot_client))
