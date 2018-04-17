import asyncio
import discord
import youtube_dl
from math import ceil
from discord.ext import commands
from Roxbot import checks
from Roxbot.load_config import owner
from Roxbot.settings import guild_settings

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': './Roxbot/cache/%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
	'before_options': '-nostdin',
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)
		self.data = data
		self.title = data.get('title')
		self.uploader = data.get("uploader")
		self.url = data.get('url')
		self.duration = data.get("duration")
		self.host = data.get("extractor_key")
		self.webpage_url = data.get('webpage_url')
		self.thumbnail_url = data.get("thumbnail", "")

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
			# TODO: Playlist Support
			# take first item from a playlist
			data = data['entries'][0]

		filename = data['url'] if stream else ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def volume_perms():
	def predicate(ctx):
		gs = guild_settings.get(ctx.guild)
		if gs.voice["need_perms"]:  # Had to copy the admin or mod code cause it wouldn't work ;-;
			if ctx.message.author.id == owner:
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


class Music:
	def __init__(self, bot):
		self.bot = bot
		# Setup variables and then add dictionary entries for all guilds the bot can see on boot-up.
		self.playlist = {}  # All audio to be played
		self.skip_votes = {}
		self.now_playing = {}  # Currently playing audio
		for guild in bot.guilds:
			self.playlist[guild.id] = []
			self.skip_votes[guild.id] = []
			self.now_playing[guild.id] = None

	async def on_guild_join(self, guild):
		"""Makes sure that when the bot joins a guild it won't need to reboot for the music bot to work."""
		self.playlist[guild.id] = []
		self.skip_votes[guild.id] = []
		self.now_playing[guild.id] = None

	@commands.command()
	async def join(self, ctx, *, channel: discord.VoiceChannel = None):
		"""Joins the voice channel your in."""
		if channel is None:
			channel = ctx.author.voice.channel

		if ctx.voice_client is not None:
			return await ctx.voice_client.move_to(channel)

		await channel.connect()

	async def queue_logic(self, ctx):
		if ctx.voice_client.source == self.now_playing[ctx.guild.id]:
			sleep_for = 0.5
			while ctx.voice_client.is_playing():
				await asyncio.sleep(sleep_for)
			if self.playlist[ctx.guild.id]:
				player = self.playlist[ctx.guild.id].pop(0)
				if player.get("stream", False) is True:
					command = self.stream
				else:
					command = self.play
				await ctx.invoke(command, url=player.get("webpage_url"))

	@commands.command(hidden=True)
	async def play_local(self, ctx, *, query):
		"""Plays a file from the local filesystem."""
		# TODO: Playlist stuff maybe
		source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
		ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

		await ctx.send('Now playing: {}'.format(query))

	@commands.cooldown(1, 0.5, commands.BucketType.guild)
	@commands.command()
	async def play(self, ctx, *, url):
		"""Plays from a url (almost anything youtube_dl supports)"""
		voice = guild_settings.get(ctx.guild).voice

		video = ytdl.extract_info(url, download=False)
		if video.get("duration", 1) > voice["max_length"] and not checks._is_admin_or_mod(ctx):
			raise commands.CommandError("Cannot play video, duration is bigger than the max duration allowed.")

		if not ctx.voice_client.is_playing() or self.now_playing[ctx.guild.id] is None:
			async with ctx.typing():
				player = await YTDLSource.from_url(url, loop=self.bot.loop)
				self.now_playing[ctx.guild.id] = player
				ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
			self.bot.loop.create_task(self.queue_logic(ctx))
			await ctx.send('Now playing: {}'.format(player.title))
		else:
			player = ytdl.extract_info(url, download=False)
			self.playlist[ctx.guild.id].append(player)
			await ctx.send("{} added to queue".format(player.get("title")))

	@commands.cooldown(1, 0.5, commands.BucketType.guild)
	@commands.command()
	async def stream(self, ctx, *, url):
		"""Streams from a url (same as yt, but doesn't predownload)"""
		if not ctx.voice_client.is_playing():
			async with ctx.typing():
				player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
				self.now_playing[ctx.guild.id] = player
				ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
			self.bot.loop.create_task(self.queue_logic(ctx))
			await ctx.send('Now playing: {}'.format(player.title))
		else:
			player = ytdl.extract_info(url, download=False)
			player["stream"] = True
			self.playlist[ctx.guild.id].append(player)
			await ctx.send("{} added to queue".format(player.get("title")))

	@play.before_invoke
	@stream.before_invoke
	@play_local.before_invoke
	async def ensure_voice(self, ctx):
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				raise commands.CommandError("Roxbot is not connected to a voice channel and couldn't auto-join a voice channel.")

	@volume_perms()
	@commands.command()
	async def volume(self, ctx, volume: int):
		"""Changes the player's volume"""
		if ctx.voice_client is None:
			raise commands.CommandError("Roxbot is not in a voice channel.")

		if 0 < volume <= 100:
			ctx.voice_client.source.volume = volume / 100
		else:
			raise commands.CommandError("Volume needs to be between 0-100%")
		return await ctx.send("Changed volume to {}%".format(volume))

	@checks.is_admin_or_mod()
	@commands.command()
	async def stop(self, ctx):
		"""Stops and disconnects the bot from voice"""
		if ctx.voice_client is None:
			raise commands.CommandError("Roxbot is not in a voice channel.")
		else:
			self.playlist[ctx.guild.id] = []
			self.now_playing[ctx.guild.id] = None
			return await ctx.voice_client.disconnect()

	@commands.command()
	async def pause(self, ctx):
		if ctx.voice_client is None:
			raise commands.CommandError("Roxbot is not in a voice channel.")
		else:
			if not ctx.voice_client.is_playing():
				return await ctx.send("Nothing is playing.")
			elif ctx.voice_client.is_paused():
				return await ctx.send("I already am paused!")
			else:
				ctx.voice_client.pause()
				return await ctx.send("Paused {}".format(ctx.voice_client.source.title))

	@commands.command()
	async def resume(self, ctx):
		if ctx.voice_client is None:
			raise commands.CommandError("Roxbot is not in a voice channel.")
		else:
			if ctx.voice_client.is_paused():
				ctx.voice_client.resume()
				return await ctx.send("Resumed {}".format(ctx.voice_client.source.title))
			else:
				if ctx.voice_client.is_playing():
					return await ctx.send("Can't resume if I'm already playing something!")
				else:
					return await ctx.send("Nothing to resume.")

	@commands.command()
	async def np(self, ctx):
		if self.now_playing[ctx.guild.id] is None:
			return await ctx.send("Nothing is playing.")
		else:
			np = ctx.voice_client.source
			embed = discord.Embed(title="Now playing: '{}' from {}".format(np.title, np.host), colour=0xDEADBF)
			embed.description = "Uploaded by: {0.uploader}\nURL: {0.webpage_url}".format(np)
			embed.set_image(url=np.thumbnail_url)
			return await ctx.send(embed=embed)

	@commands.command()
	async def skip(self, ctx):
		voice = guild_settings.get(ctx.guild).voice
		if ctx.voice_client.is_playing():
			if voice["skip_voting"]:
				if ctx.author in self.skip_votes[ctx.guild.id]:
					return await ctx.send("You have already voted to skip the current track.")
				else:
					self.skip_votes[ctx.guild.id].append(ctx.author)
					# -1 due to the bot being counted in the members generator
					ratio = len(self.skip_votes[ctx.guild.id]) / (len(ctx.voice_client.channel.members) - 1)
					needed_users = ceil(len(ctx.voice_client.channel.members) * voice["skip_ratio"]) - 1
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

	# TODO: Playlist, Queue, Skip Votes commands
	# TODO: Speed Improvements, better cooldown, reduce errors
	# TODO: Better documentation
	# TODO: Clean up outputs
	# TODO: Maybe autoclean the cache

def setup(bot_client):
	bot_client.add_cog(Music(bot_client))
