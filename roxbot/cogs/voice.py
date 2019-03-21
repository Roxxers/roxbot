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


import asyncio
import datetime
import os
from math import ceil

import discord
import youtube_dl
from discord.ext import commands

import roxbot
from roxbot.db import *

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


class VoiceSingle(db.Entity):
    need_perms = Required(bool, default=False)
    skip_voting = Required(bool, default=False)
    skip_ratio = Required(float, default=0.6, py_check=lambda v: 0 <= v <= 1)
    max_length = Required(int, default=600)
    guild_id = Required(int, size=64, unique=True)


def need_perms():
    def predicate(ctx):
        with db_session:
            settings = VoiceSingle.get(guild_id=ctx.guild.id)
        if settings.need_perms:
            return roxbot.utils.has_permissions_or_owner(ctx, manage_channels=True)
        else:
            return True
    return commands.check(predicate)


class NowPlayingEmbed(discord.Embed):
    def __init__(self, **kwargs):
        image = kwargs.pop("image", None)
        thumbnail = kwargs.pop("thumbnail", None)
        footer = kwargs.pop("footer", None)

        super().__init__(**kwargs)

        if thumbnail:
            super().set_thumbnail(url=thumbnail)
        if footer:
            super().set_footer(text=footer)
        if image:
            super().set_image(url=image)

    @staticmethod
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

    @classmethod
    def make(cls, now_playing, playing_status):
        np = now_playing
        title = "{0}: '{1.title}' from {1.host}".format(playing_status, now_playing)
        duration = cls._format_duration(np.duration)
        time_played = cls._format_duration(np.source.timer / 1000)
        description = """Uploaded by: [{0.uploader}]({0.uploader_url})
        URL: [Here]({0.webpage_url})
        Duration: {1}
        Queued by: {0.queued_by}""".format(now_playing, duration)
        image = np.thumbnail_url
        footer_text = "{}/{} | Volume: {}%".format(time_played, duration, int(now_playing.volume * 100))
        return cls(
            title=title,
            url=np.webpage_url,
            description=description,
            colour=roxbot.EmbedColours.pink,
            image=image,
            footer=footer_text
        )


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


class Voice(commands.Cog):
    """The Voice cog is a cog that adds and manages a fully-functional music bot for Roxbot."""
    # TODO: Add voting to many of the commands.
    def __init__(self, bot):
        # Auto Cleanup cache files on boot
        self._clear_cache()

        # Setup variables and then add dictionary entries for all guilds the bot can see on boot-up.
        self.bot = bot
        self.autogen_db = VoiceSingle
        # TODO: Make this into a on roxbot joining voice thing instead of generating this for all servers on boot.
        self.refresh_rate = 1/60  # 60hz
        self._volume = {}
        self.playlist = {}  # All audio to be played
        self.skip_votes = {}
        self.am_queuing = {}
        self.now_playing = {}  # Currently playing audio
        self.queue_logic = {}
        self.bot.add_listener(self._create_dicts, "on_ready")

    async def _create_dicts(self):
        # TODO: Probably still move this to be dynamic but that might be weird with discord connection issues.
        for guild in self.bot.guilds:
            self._volume[guild.id] = 0.2
            self.playlist[guild.id] = []
            self.skip_votes[guild.id] = []
            self.am_queuing[guild.id] = False
            self.now_playing[guild.id] = None
            self.queue_logic[guild.id] = None

    @staticmethod
    def _clear_cache():
        """Clears the cache folder for the music bot. Ignores the ".gitignore" file to avoid deleting versioned files."""
        for file in os.listdir("roxbot/cache"):
            if file != ".gitignore":
                os.remove("roxbot/cache/{}".format(file))

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

    @roxbot.checks.has_permissions_or_owner(manage_channels=True)
    @commands.guild_only()
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Summon Roxbot to a voice channel, usually the one you are currently in.

        This is done automatically when you execute the `;play` or `;stream` commands.

        Options:

            - `Voice Channel` - OPTIONAL. The name of a Voice Channel

        Example:
            # Join a voice channle called General
            ;join General
        """
        # Get channel
        if channel is None:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise roxbot.UserError("Failed to join voice channel. Please specify a channel or join one for Roxbot to join.")

        # Join VoiceChannel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        return await ctx.send("Joined {0.name} :ok_hand:".format(channel))

    async def _play(self, ctx, url, stream, queued_by):
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=stream, volume=self._volume[ctx.guild.id])
        player.stream = stream
        player.queued_by = queued_by or ctx.author
        self.now_playing[ctx.guild.id] = player
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        # Create task to deal with what to do when the video ends or is skipped and how to handle the queue
        self.queue_logic[ctx.guild.id] = self.bot.loop.create_task(self._queue_logic(ctx))

    @commands.guild_only()
    @commands.cooldown(1, 0.8, commands.BucketType.guild)
    @commands.command(aliases=["yt"])
    async def play(self, ctx, *, url, stream=False, from_queue=False, queued_by=None):
        """Plays a video over voice chat using the given URL. This URL has to be one that YoutubeDL can download from. [A list can be found here.](https://rg3.github.io/youtube-dl/supportedsites.html)

        If the bot is already playing something, this will be queued up to be played later. If you want to play a livestream, use the `;stream` command.

        The user needs to be in a voice channel for this command to work. This is ignored if the user has the `manage_channels` permission. There is also a duration limit that can be placed on videos. This is also ignored if the user has the `manage_channels` permission.


        Options:

            - `url` -  A url to a video or playlist or a search term. If a playlist, it will play the first video and queue up all other videos in the playlist. If just text, Roxbot will play the first Youtube search result.

        Examples:
            # Play the quality youtube video
            ;play https://www.youtube.com/watch?v=3uOPGkEJ56Q
        """
        guild = ctx.guild
        with db_session:
            max_duration = VoiceSingle.get(guild_id=guild.id).max_length

        # Checks if invoker is in voice with the bot. Skips admins and mods and owner and if the song was queued previously.
        if not (roxbot.utils.has_permissions_or_owner(ctx, manage_channels=True) or from_queue):
            if not ctx.author.voice:
                raise roxbot.UserError("You're not in the same voice channel as Roxbot.")
            if ctx.author.voice.channel != ctx.voice_client.channel:
                raise roxbot.UserError("You're not in the same voice channel as Roxbot.")

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
        if video.get("duration", 1) > max_duration and not roxbot.utils.has_permissions_or_owner(ctx, manage_channels=True):
            raise roxbot.UserError("Cannot play video, duration is bigger than the max duration allowed.")

        # Actual playing stuff section.
        # If not playing and not queuing, and not paused, play the song. Otherwise queue it.
        if (not ctx.voice_client.is_playing() and self.am_queuing[guild.id] is False) and not ctx.voice_client.is_paused():
            self.am_queuing[guild.id] = True
            async with ctx.typing():
                await self._play(ctx, url, stream, queued_by)
            self.am_queuing[ctx.guild.id] = False

            embed = NowPlayingEmbed.make(self.now_playing[ctx.guild.id], "Now Playing")
            await ctx.send(embed=embed)
        else:
            # Queue the song as there is already a song playing or paused.
            self._queue_song(ctx, video, stream)

            # Sleep because if not, queued up things will send first and probably freak out users or something
            while self.am_queuing[guild.id] is True:
                await asyncio.sleep(self.refresh_rate)
            embed = discord.Embed(description='Added "{}" to queue'.format(video.get("title")), colour=roxbot.EmbedColours.pink)
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.cooldown(1, 0.5, commands.BucketType.guild)
    @commands.command()
    async def stream(self, ctx, *, url):
        """
        A version of `;play` that should be used to stream livestreams or internet radio sources.

        For more details on how this command words, please look at the documentation for the `;play` command.
        """
        # Just invoke the play command with the stream argument as true. Deals with everything else anyway.
        return await ctx.invoke(self.play, url=url, stream=True)

    @need_perms()
    @commands.guild_only()
    @commands.command()
    async def volume(self, ctx, volume: int):
        """
        Sets the volume percentage for Roxbot's audio.

        The current volume of Roxbot is displayed by her nowplaying rich embeds that are displayed when she begins to play a video or when the `;nowplaying` command is used.

        Options:

            - `percent` - A positive integer between 0-100 representing a percentage.

        Example:
            # Set volume to 20%
            ;volume 20
        """
        if 0 <= volume <= 100:
            ctx.voice_client.source.volume = volume / 100  # Volume needs to be a float between 0 and 1... kinda
            self._volume[ctx.guild.id] = volume / 100  # Volume needs to be a float between 0 and 1... kinda
        else:
            raise roxbot.UserError("Volume needs to be between 0-100%")
        return await ctx.send("Changed volume to {}%".format(volume))

    @need_perms()
    @commands.guild_only()
    @commands.cooldown(1, 2)
    @commands.command()
    async def pause(self, ctx):
        """Pauses the current video, if playing."""
        if ctx.voice_client.is_paused():
            return await ctx.send("I already am paused!")
        else:
            ctx.voice_client.pause()
            return await ctx.send("Paused '{}'".format(ctx.voice_client.source.title))

    @need_perms()
    @commands.guild_only()
    @commands.cooldown(1, 2)
    @commands.command()
    async def resume(self, ctx):
        """Resumes the bot, if paused."""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            return await ctx.send("Resumed '{}'".format(ctx.voice_client.source.title))
        else:
            if ctx.voice_client.is_playing():
                return await ctx.send("Can't resume if I'm already playing something!")
            else:
                return await ctx.send("Nothing to resume.")

    @commands.guild_only()
    @commands.command()
    async def skip(self, ctx, option=""):
        """Skips the current playing video.

        If skipvoting is enabled, multiple people will have to use this command to go over the ratio that is also set by server moderators.

        Options:
            - `--force` - if skip voting is enabled, users with the `manage_channel` permission can skip this process and for the video to be skipped.

        Examples:
            # Vote to skip a video
            ;skip
            # Force skip a video
            ;skip --force
        """
        with db_session:
            voice = VoiceSingle.get(guild_id=ctx.guild.id)
        if voice.skip_voting and not (option == "--force" and ctx.author.guild_permissions.manage_channels):  # Admin force skipping
            if ctx.author in self.skip_votes[ctx.guild.id]:
                return await ctx.send("You have already voted to skip the current track.")
            else:
                self.skip_votes[ctx.guild.id].append(ctx.author)
                # -1 due to the bot being counted in the members generator
                ratio = len(self.skip_votes[ctx.guild.id]) / (len(ctx.voice_client.channel.members) - 1)
                needed_users = ceil((len(ctx.voice_client.channel.members) - 1) * voice.skip_ratio)
                if ratio >= voice.skip_ratio:
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


    @commands.guild_only()
    @commands.command(aliases=["np"])
    async def nowplaying(self, ctx):
        """Displays what is currently playing."""
        if self.now_playing[ctx.guild.id] is None:
            return await ctx.send("Nothing is playing.")
        else:
            if ctx.voice_client.is_paused():
                x = "Paused"
            else:
                x = "Now Playing"
            embed = NowPlayingEmbed.make(self.now_playing[ctx.guild.id], x)
            return await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def queue(self, ctx):
        """Displays what videos are queued up and waiting to be played."""
        paginator = commands.Paginator(prefix="", suffix="")
        index = 1

        if not self.playlist[ctx.guild.id]:
            return await ctx.send("Nothing is up next. Maybe you should add something!")
        else:
            for video in self.playlist[ctx.guild.id]:
                paginator.add_line("{}) '{}' queued by {}\n".format(index, video["title"], video["queued_by"]))
                index += 1
        if len(paginator.pages) <= 1:
            embed = discord.Embed(title="Queue", description=paginator.pages[0], colour=roxbot.EmbedColours.pink)
            return await ctx.send(embed=embed)
        else:
            pages = []
            pages.append(discord.Embed(title="Queue", description=paginator.pages.pop(0), colour=roxbot.EmbedColours.pink))
            for page in paginator.pages:
                pages.append(discord.Embed(description=page, colour=roxbot.EmbedColours.pink))
            for page in pages:
                await ctx.send(embed=page)

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.command()
    async def remove(self, ctx, index):
        """Removes a item from the queue with the given index.

        Options:
            - `index/all` - A number representing an index in the queue to remove one video, or "all" to clear all videos.

        Examples:
            # Remove 2nd video
            ;remove 2
            # Clear the queue
            ;remove all
        """
        # Try and convert index into an into. If not possible, just move forward
        try:
            index = int(index)
        except ValueError:
            pass

        # If not str "all" or an int, raise error.
        if index != "all" and not isinstance(index, int):
            raise roxbot.UserError("No valid option given.")
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
                raise roxbot.UserError("Valid Index not given.")

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.command(alaises=["disconnect"])
    async def stop(self, ctx):
        """Stops Roxbot from playing music and has her leave voice chat."""
        # Clear up variables before stopping.
        self.playlist[ctx.guild.id] = []
        self.now_playing[ctx.guild.id] = None
        self.queue_logic[ctx.guild.id].cancel()
        await ctx.voice_client.disconnect()
        return await ctx.send(":wave:")

    @play.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        """Ensures the bot is in a voice channel before continuing and if it cannot auto join, raise an error."""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                raise roxbot.UserError("Roxbot is not connected to a voice channel and couldn't auto-join a voice channel.")

    @skip.before_invoke
    @stop.before_invoke
    @pause.before_invoke
    @resume.before_invoke
    @volume.before_invoke
    async def check_in_voice(self, ctx):
        if ctx.voice_client is None:
            raise roxbot.UserError("Roxbot is not in a voice channel.")

    @skip.before_invoke
    @pause.before_invoke
    async def check_playing(self, ctx):
        try:
            if not ctx.voice_client.is_playing():
                raise roxbot.UserError("I'm not playing anything.")
        except AttributeError:
            raise roxbot.UserError("I'm not playing anything.")

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.command()
    async def voice(self, ctx, setting=None, change=None):
        """Edits settings for the voice cog.

        Options:
            - `enable/disable`: Enable/disables specified change.
            - `skipratio`: Specify what the ratio should be for skip voting if enabled. Example: 0.6 for 60%
            - `maxlength/duration`: Specify (in seconds) the max duration of a video that can be played.

        Possible settings to enable/disable:
            - `needperms`: specifies whether `volume`, `pause`, or `resume` require permissions or not.
            - `skipvoting`: enables voting to skip instead of one user skipping.

        Example:
            # Enable skipvoting
            ;voice enable skip_voting
            # Disbale needing perms for volume, pause, etc.
            ;voice disable need_perms
            # Edit max_length to 5 minutes
            ;voice max_length 300
        """
        setting = setting.lower()
        change = change.lower()

        with db_session:
            voice = VoiceSingle.get(guild_id=ctx.guild.id)
            if setting == "enable":
                if change in ("needperms", "need_perms"):
                    voice.need_perms = True
                    await ctx.send("'{}' has been enabled!".format(change))
                elif change in ("skipvoting", "skip_voting"):
                    voice.skip_voting = True
                    await ctx.send("'{}' has been enabled!".format(change))
                else:
                    return await ctx.send("Not a valid change.")
            elif setting == "disable":
                if change in ("skipvoting", "skip_voting"):
                    voice.need_perms = False
                    await ctx.send("'{}' was disabled :cry:".format(change))
                elif change in ("skipvoting", "skip_voting"):
                    voice.skip_voting = False
                    await ctx.send("'{}' was disabled :cry:".format(change))
                else:
                    return await ctx.send("Not a valid change.")
            elif setting in ("skipratio", "skip_ratio"):
                change = float(change)
                if 1 > change > 0:
                    voice.skip_ratio = change
                elif 0 < change <= 100:
                    change = change/10
                    voice.skip_ratio = change
                else:
                    return await ctx.send("Valid ratio not given.")
                await ctx.send("Skip Ratio was set to {}".format(change))
            elif setting in ("maxlength", "max_length"):
                change = int(change)
                if change >= 1:
                    voice.max_length = change
                else:
                    return await ctx.send("Valid max duration not given.")
                await ctx.send("Max Duration was set to {}".format(change))
            else:
                return await ctx.send("Valid option not given.")


def setup(bot_client):
    bot_client.add_cog(Voice(bot_client))
