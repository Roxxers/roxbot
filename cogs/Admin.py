import sys
import os

from config.config import Config
from main import owner_id

import discord
from discord.ext.commands import bot


def owner(ctx):
    return owner_id == ctx.message.author.id


class Admin():
    def __init__(self, Bot):
        self.bot = Bot
        self.con = Config(Bot)

    @bot.command(pass_context=True)
    async def blacklist(self, ctx, option, *args):
        """
        Usage:
            .blacklist [ + | - | add | remove ] @UserName [@UserName2 ...]

        Add or remove users to the blacklist.
        Blacklisted users are forbidden from using bot commands.
        Only the bot owner can use this command
        """
        if not owner(ctx):
            return await self.bot.reply("You do not have permission to do this command.", delete_after=20)
        blacklist_amount = 0
        mentions = ctx.message.mentions

        if not mentions:
            return await self.bot.say("You didn't mention anyone")

        if option not in ['+', '-', 'add', 'remove']:
            return await self.bot.say('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

        for user in mentions:
            if user.id == owner_id:
                print("[Commands:Blacklist] The owner cannot be blacklisted.")
                await self.bot.say("The owner cannot be blacklisted.")
                mentions.remove(user)

        if option in ['+', 'add']:
            with open("config/blacklist.txt", "r") as fp:
                for user in mentions:
                    for line in fp.readlines():
                        if user.id + "\n" in line:
                            mentions.remove(user)

            with open("config/blacklist.txt", "a+") as fp:
                lines = fp.readlines()
                for user in mentions:
                    if user.id not in lines:
                        fp.write("{}\n".format(user.id))
                        blacklist_amount += 1
            return await self.bot.say('{} user(s) have been added to the blacklist'.format(blacklist_amount))

        elif option in ['-', 'remove']:
            with open("config/blacklist.txt", "r") as fp:
                lines = fp.readlines()
            with open("config/blacklist.txt", "w") as fp:
                for user in mentions:
                    for line in lines:
                        if user.id + "\n" != line:
                            fp.write(line)
                        else:
                            fp.write("")
                            blacklist_amount += 1
                return await self.bot.say('{} user(s) have been removed from the blacklist'.format(blacklist_amount))


    @bot.command(pass_context=True)
    async def enablesetting(self, ctx, setting):
        if not owner(ctx):
            return await self.bot.reply("You do not have permission to do this command.", delete_after=20)
        else:
            if module in self.con.serverconfig[ctx.message.server.id]:
                if not self.con.serverconfig[ctx.message.server.id][setting]["enabled"]:
                    self.con.serverconfig[ctx.message.server.id][setting]["enabled"] = 1
                    self.con.updateconfig(self.con.serverconfig)
                    return await self.bot.say("'{}' was enabled!".format(setting))
                else:
                    self.con.serverconfig[ctx.message.server.id][setting]["enabled"] = 0
                    self.con.updateconfig(self.con.serverconfig)
                    return await self.bot.say("'{}' was disabled :cry:".format(setting))
            else:
                return await self.bot.say("That module dont exist fam. You made the thing")

    @bot.command(pass_context=True)
    async def set_welcomechannel(self, ctx, channel: discord.Channel = None):
        if not owner(ctx):
            return await self.bot.reply("You do not have permission to do this command.", delete_after=20)
        self.con.serverconfig[ctx.message.server.id]["greets"]["welcome-channel"] = channel.id
        self.con.updateconfig(self.con.serverconfig)
        return await self.bot.say("{} has been set as the welcome channel!".format(channel.mention))

    @bot.command(pass_context=True)
    async def set_goodbyechannel(self, ctx, channel: discord.Channel = None):
        if not owner(ctx):
            return await self.bot.reply("You do not have permission to do this command.", delete_after=20)
        self.con.serverconfig[ctx.message.server.id]["goodbyes"]["goodbye-channel"] = channel.id
        self.con.updateconfig(self.con.serverconfig)
        return await self.bot.say("{} has been set as the goodbye channel!".format(channel.mention))

    @bot.command(pass_context=True)
    async def set_twitchchannel(self, ctx, channel: discord.Channel = None):
        if not owner(ctx):
            return await self.bot.reply("You do not have permission to do this command.", delete_after=20)
        self.con.serverconfig[ctx.message.server.id]["twitch_shilling"]["twitch-channel"] = channel.id
        self.con.updateconfig(self.con.serverconfig)
        return await self.bot.say("{} has been set as the twitch shilling channel!".format(channel.mention))

    @bot.command()
    async def restart(self):
        await self.bot.logout()
        return os.execl(sys.executable, sys.executable, *sys.argv)

    @bot.command()
    async def shutdown(self):
        await self.bot.logout()
        return exit(0)


def setup(Bot):
    Bot.add_cog(Admin(Bot))
