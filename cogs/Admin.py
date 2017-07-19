import os
import sys
import aiohttp
import asyncio

from main import owner_id
from config.config import Config

import discord
from discord.ext.commands import bot


def owner(ctx):
    return owner_id == ctx.message.author.id


class Admin():
    def __init__(self, Bot):
        self.bot = Bot
        self.con = Config(Bot)

    @bot.command(pass_context=True, hidden=True)
    async def blacklist(self, ctx, option, *args):
        """
        Usage:
            .blacklist [ + | - | add | remove ] @UserName [@UserName2 ...]

        Add or remove users to the blacklist.
        Blacklisted users are forbidden from using bot commands.
        Only the bot owner can use this command
        """
        if not owner(ctx):
            return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
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


    @bot.command(pass_context=True, hidden=True)
    async def enablesetting(self, ctx, setting):
        if not owner(ctx):
            return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
        else:
            if setting in self.con.serverconfig[ctx.message.server.id]:
                if not self.con.serverconfig[ctx.message.server.id][setting]["enabled"]:
                    self.con.serverconfig[ctx.message.server.id][setting]["enabled"] = 1
                    self.con.updateconfig()
                    return await self.bot.say("'{}' was enabled!".format(setting))
                else:
                    self.con.serverconfig[ctx.message.server.id][setting]["enabled"] = 0
                    self.con.updateconfig()
                    return await self.bot.say("'{}' was disabled :cry:".format(setting))
            else:
                return await self.bot.say("That module dont exist fam. You made the thing")

    @bot.command(pass_context=True, hidden=True)
    async def set_welcomechannel(self, ctx, channel: discord.Channel = None):
        if not owner(ctx):
            return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
        self.con.serverconfig[ctx.message.server.id]["greets"]["welcome-channel"] = channel.id
        self.con.updateconfig()
        return await self.bot.say("{} has been set as the welcome channel!".format(channel.mention))

    @bot.command(pass_context=True, hidden=True)
    async def set_goodbyechannel(self, ctx, channel: discord.Channel = None):
        if not owner(ctx):
            return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
        self.con.serverconfig[ctx.message.server.id]["goodbyes"]["goodbye-channel"] = channel.id
        self.con.updateconfig()
        return await self.bot.say("{} has been set as the goodbye channel!".format(channel.mention))

    @bot.command(pass_context=True, hidden=True)
    async def set_twitchchannel(self, ctx, channel: discord.Channel = None):
        if not owner(ctx):
            return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
        self.con.serverconfig[ctx.message.server.id]["twitch_shilling"]["twitch-channel"] = channel.id
        self.con.updateconfig()
        return await self.bot.say("{} has been set as the twitch shilling channel!".format(channel.mention))

    @bot.command(pass_context=True, visible=False)
    async def set_customwelcomemessage(self, ctx, *message):
        self.con.serverconfig[ctx.message.server.id]["greets"]["custom_message"] = ' '.join(message)
        self.con.updateconfig()
        return await self.bot.say("Custom message set to '{}'".format(' '.join(message)), delete_after=10)

    @bot.command(pass_context=True, hidden=True)
    async def changeavatar(self, ctx, url=None):
        """
        Usage:
            {command_prefix}setavatar [url]

        Changes the bot's avatar.
        Attaching a file and leaving the url parameter blank also works.
        """
        if not owner(ctx):
            return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)

        if ctx.message.attachments:
            thing = ctx.message.attachments[0]['url']
        else:
            thing = url.strip('<>')

        tempAvaFile = 'tempAva.png'
        async with aiohttp.get(thing) as img:
            with open(tempAvaFile, 'wb') as f:
                f.write(await img.read())
        with open(tempAvaFile, 'rb') as f:
            await self.bot.edit_profile(avatar=f.read())
        os.remove(tempAvaFile)
        asyncio.sleep(2)
        return await self.bot.say(":ok_hand:")

    @bot.command(hidden=True)
    async def restart(self, ctx):
        if not owner(ctx):
            return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)

        await self.bot.logout()
        return os.execl(sys.executable, sys.executable, *sys.argv)

    @bot.command(hidden=True)
    async def shutdown(self, ctx):
        if not owner(ctx):
            return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)

        await self.bot.logout()
        return exit(0)

    @bot.command(pass_context=True, hidden=True)
    async def announce(self, ctx, *announcement):
        """
        ONLY USE FOR SERIOUS ANNOUNCEMENTS
        """
        if not owner(ctx):
            return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)

        embed = discord.Embed(title="RoxBot Announcement", colour=discord.Colour(0x306f99), description=' '.join(announcement))
        embed.set_footer(text="This message has be automatically generated by a QT Roxie",
                         icon_url=self.bot.user.avatar_url)
        for server in self.bot.servers:
            await self.bot.send_message(server, embed=embed)
        return await self.bot.say("Done!", delete_after=self.con.delete_after)


def setup(Bot):
    Bot.add_cog(Admin(Bot))
