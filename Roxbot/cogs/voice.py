import asyncio
import discord
import youtube_dl
from discord.ext import commands

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


def volume_perms():
	def predicate(ctx):
		gs = guild_settings.get(ctx.guild)
		if gs.voice["need_perms"]: # Had to copy the admin or mod code cause it wouldn't work ;-;
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


class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)
		self.data = data
		self.title = data.get('title')
		self.url = data.get('url')
		self.webpage_url = data.get('webpage_url')
		self.duration = data.get("duration")

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


class Music:
	def __init__(self, bot):
		self.bot = bot
		self.playlist = {}
		self.is_skipped = {}
		for guild in bot.guilds:
			self.playlist[guild.id] = []
		self.now_playing = None

	# TODO: Better documentation

	@commands.command()
	async def join(self, ctx, *, channel: discord.VoiceChannel = None):
		"""Joins the voice channel your in."""
		if channel is None:
			channel = ctx.author.voice.channel

		if ctx.voice_client is not None:
			return await ctx.voice_client.move_to(channel)

		await channel.connect()

	@commands.command(hidden=True)
	async def play_local(self, ctx, *, query):
		"""Plays a file from the local filesystem."""
		# TODO: Playlist stuff
		source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
		ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

		await ctx.send('Now playing: {}'.format(query))

	@commands.command()
	async def play(self, ctx, *, url):
		"""Plays from a url (almost anything youtube_dl supports)"""
		if not ctx.voice_client.is_playing():
			async with ctx.typing():
				player = await YTDLSource.from_url(url, loop=self.bot.loop)
				self.now_playing = player
				ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

			await ctx.send('Now playing: {}'.format(player.title))
		else:
			player = await YTDLSource.from_url(url, loop=self.bot.loop)
			self.playlist[ctx.guild.id].append(player)
			await ctx.send("{} added to queue".format(player.title))

	@play.after_invoke
	async def while_playing(self, ctx):
		if ctx.voice_client.source == self.now_playing:
			count = 0
			sleep_for = 0.5
			while ctx.voice_client.is_playing():
				await asyncio.sleep(sleep_for)
				count += sleep_for
			if self.playlist[ctx.guild.id]:
				player = self.playlist[ctx.guild.id].pop(0)
				await ctx.invoke(self.play, url=player.webpage_url)

	@commands.command()
	async def stream(self, ctx, *, url):
		"""Streams from a url (same as yt, but doesn't predownload)"""

		async with ctx.typing():
			player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
			ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

		await ctx.send('Now playing: {}'.format(player.title))

	@volume_perms()
	@commands.command()
	async def volume(self, ctx, volume: int):
		"""Changes the player's volume"""
		if ctx.voice_client is None:
			return await ctx.send("Not connected to a voice channel.")

		if volume > 0 and volume <= 100:
			ctx.voice_client.source.volume = volume / 100
		else:
			raise commands.CommandError("Volume needs to be between 0-100%")
		return await ctx.send("Changed volume to {}%".format(volume))

	@commands.command()
	async def stop(self, ctx):
		"""Stops and disconnects the bot from voice"""
		self.now_playing = None
		await ctx.voice_client.disconnect()

	# TODO: Pause command

	@commands.command()
	async def skip(self, ctx):
		# This should be fine as the while_playing function should handle moving to the next song.
		# TODO: Needs voting logic preferably in the future
		if ctx.voice_client.is_playing():
			self.now_playing = None
			ctx.voice_client.stop()
			# TODO: Title detection
			return await ctx.send("Skipped song")
		else:
			await ctx.send("I'm not playing anything.")

	# TODO: Skip command. That will also need to check for the waiting for the song to be over function

	@play.before_invoke
	@play_local.before_invoke
	@stream.before_invoke
	async def ensure_voice(self, ctx):
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				raise commands.CommandError("Author not connected to a voice channel.")


def setup(bot_client):
	bot_client.add_cog(Music(bot_client))
