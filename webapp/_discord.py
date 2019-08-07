import discord
import threading
import asyncio


def start_loop(loop, gen):
    loop.run_until_complete(gen)


class DiscordAccessor:
    discord_loop = asyncio.new_event_loop()
    client = discord.Client(loop=discord_loop)

    def start(self):
        from webapp import app
        self.discord_coroutine = DiscordAccessor.client.start(app.config["DISCORD_TOKEN"])
        self.discord_thread = threading.Thread(target=start_loop, args=(self.discord_loop, self.discord_coroutine))
        self.discord_thread.start()


bot = DiscordAccessor()
