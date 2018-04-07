import asyncio
import discord
import youtube_dl
from discord.ext import commands

# Can't pretend I wrote most of this. It's mostly copied from the example given in Discord.py. Then edited because the example was basic ofc.
# And like actually getting it to play was too complicated for me to care. But I don't mind working on it past
# getting the bot to play the thing.

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
		self.url = data.get('url')
		self.duration = data.get("duration")

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0] # TODO: Playlist Support

		filename = data['url'] if stream else ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music:
	def __init__(self, bot):
		self.bot = bot
		self.playlist = {}
		for guild in bot.guilds:
			self.playlist[guild.id] = []
		self.now_playing = None

	@commands.command()
	async def join(self, ctx, *, channel: discord.VoiceChannel = None):
		"""Joins the voice channel your in, """
		if channel is None:
			channel = ctx.author.voice.channel

		if ctx.voice_client is not None:
			return await ctx.voice_client.move_to(channel)

		await channel.connect()

	@commands.command(hidden=True)
	async def play_local(self, ctx, *, query):
		"""Plays a file from the local filesystem"""
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
		await asyncio.sleep(ctx.voice_client.source.duration)
		if self.playlist[ctx.guild.id]:
			while ctx.voice_client.is_playing():
				await asyncio.sleep(.1) # Just in case of some lag or or something

			player = self.playlist[ctx.guild.id].pop(0)
			await ctx.invoke(self.play, url=player.url)

	@commands.command()
	async def stream(self, ctx, *, url):
		"""Streams from a url (same as yt, but doesn't predownload)"""

		async with ctx.typing():
			player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
			ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

		await ctx.send('Now playing: {}'.format(player.title))

	@commands.command()
	async def volume(self, ctx, volume: int):
		"""Changes the player's volume"""
		# TODO: Permission based usage. maybe set in guild settings.
		if ctx.voice_client is None:
			return await ctx.send("Not connected to a voice channel.")

		ctx.voice_client.source.volume = volume / 100
		await ctx.send("Changed volume to {}%".format(volume))

	@commands.command()
	async def stop(self, ctx):
		"""Stops and disconnects the bot from voice"""

		await ctx.voice_client.disconnect()

	# TODO: Pause command
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
