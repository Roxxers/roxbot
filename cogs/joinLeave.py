import discord

from config.config import Config

class joinLeave():
    def __init__(self, Bot):
        self.bot = Bot
        self.con = Config(Bot)

    async def on_member_join(self, member):
        """
        Greets users when they join a server. 
        """
        # TODO: Move these to a cog cause they suck in main
        self.con.load_config()
        if not self.con.serverconfig[member.server.id]["greets"]["enabled"]:
            return
        if self.con.serverconfig[member.server.id]["greets"]["custom-message"]:
            message = self.con.serverconfig[member.server.id]["greets"]["custom-message"]
        else:
            message = self.con.serverconfig[member.server.id]["greets"]["default-message"]
        # TODO: Maybe thumbnail for the embed
        em = discord.Embed(
            title="Welcome to {}!".format(member.server),
            description='Hey {}! Welcome to **{}**! {}'.format(member.mention, member.server, message),
            colour=0xDEADBF)

        if self.con.serverconfig[member.server.id]["greets"]["welcome-channel"]:
            channel = discord.Object(self.con.serverconfig[member.server.id]["greets"]["welcome-channel"])
        else:
            channel = member.server.default_channel
        return await self.bot.send_message(channel,embed=em)

    async def on_member_remove(self, member):
        self.con.load_config()
        if not self.con.serverconfig[member.server.id]["goodbyes"]["enabled"]:
            return
        else:
            return await self.bot.send_message(member.server,embed=discord.Embed(
                description="{}#{} has left or been beaned.".format(member.name, member.discriminator), colour=0xDEADBF))

def setup(Bot):
    Bot.add_cog(joinLeave(Bot))
