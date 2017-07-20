from discord.ext.commands import bot
import discord
from main import blacklisted
from cogs.Admin import owner
from config.config import Config


class Twitch():
    def __init__(self, bot):
        self.bot = bot
        self.con = Config(bot)

    async def on_member_update(self, member_b, member_a):
        # Twitch Shilling Part
        if blacklisted(member_b):
            return
        if member_a.game:
            if member_a.game.type and not member_b.game.type:
                ts_enabled = self.con.serverconfig[member_a.server.id]["twitch"]["enabled"]
                ts_whitelist = self.con.serverconfig[member_a.server.id]["twitch"]["whitelist"]["enabled"]
                if ts_enabled:
                    if not ts_whitelist or member_a.id in \
                            self.con.serverconfig[member_a.server.id]["twitch"]["whitelist"]["list"]:
                        channel = discord.Object(self.con.serverconfig[member_a.server.id]["twitch"]["twitch-channel"])
                        return await self.bot.send_message(channel,
                                                           content=":video_game:** {} is live!** :video_game:\n{}\n{}".format(
                                                               member_a.name, member_a.game.name, member_a.game.url))

    @bot.command(pass_context=True, hidden=True)
    async def ts_enablewhitelist(self, ctx):
        if not owner(ctx):
            return await self.bot.reply("You do not have permission to do this command.", delete_after=20)
        else:
            self.con.serverconfig = self.con.load_config()
            if not self.con.serverconfig[ctx.server.id]["twitch"]["whitelist"]["enabled"]:
                self.con.serverconfig[ctx.server.id]["twitch"]["whitelist"]["enabled"] = 1
                self.con.updateconfig()
                return await self.bot.reply("Whitelist for Twitch shilling has been enabled.")
            else:
                self.con.serverconfig[ctx.server.id]["twitch"]["whitelist"]["enabled"] = 0
                self.con.updateconfig()
                return await self.bot.reply("Whitelist for Twitch shilling has been disabled.")

    @bot.command(pass_context=True, hidden=True)
    async def ts_whitelist(self, ctx, option, *mentions):
        if not owner(ctx):
            return await self.bot.reply("You do not have permission to do this command.", delete_after=20)

        whitelist_count = 0

        if not ctx.message.mentions and option != 'list':
            return await self.bot.reply("You haven't mentioned anyone to whitelist.")

        if option not in ['+', '-', 'add', 'remove', 'list']:
            return await self.bot.say('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

        if option in ['+', 'add']:
            self.con.serverconfig = self.con.load_config()
            for user in ctx.message.mentions:
                self.con.serverconfig[ctx.message.server.id]["twitch"]["whitelist"]["list"].append(user.id)
                self.con.updateconfig()
                whitelist_count += 1
            return await self.bot.say('{} user(s) have been added to the whitelist'.format(whitelist_count))

        elif option in ['-', 'remove']:
            self.con.serverconfig = self.con.load_config()
            for user in ctx.message.mentions:
                if user.id in self.con.serverconfig[ctx.message.server.id]["twitch"]["whitelist"]["list"]:
                    self.con.serverconfig[ctx.message.server.id]["twitch"]["whitelist"]["list"].remove(user.id)
                    self.con.updateconfig()
                    whitelist_count += 1
            return await self.bot.say('{} user(s) have been removed to the whitelist'.format(whitelist_count))

        elif option == 'list':
            return await self.bot.say(
                self.con.serverconfig[ctx.message.server.id]["twitch"]["whitelist"]["list"])


def setup(bot):
    bot.add_cog(Twitch(bot))
