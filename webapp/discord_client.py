import discord
import threading
import asyncio
from webapp import config, app



def start_loop(loop, gen):
    loop.run_until_complete(gen)


class DiscordAccessor:
    discord_loop = asyncio.new_event_loop()
    client = discord.Client(loop=discord_loop)

    def __init__(self):
        self.channel_id = 'channelID'

        self.discord_coroutine = DiscordAccessor.client.start(config["Tokens"]["Discord"])

        self.discord_thread = threading.Thread(target=start_loop, args=(self.discord_loop, self.discord_coroutine))
        self.discord_thread.start()


bot = DiscordAccessor()

