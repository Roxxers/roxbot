from discord.ext.commands import bot
import discord

from main import owner_id
from config.config import Config


def owner(ctx):
    return owner_id == ctx.message.author.id


class selfAssign():
    def __init__(self, Bot):
        self.bot = Bot
        self.con = Config(Bot)

    @bot.command(pass_context=True)
    async def listroles(self, ctx):
        roles = []
        for role in self.con.serverconfig[ctx.message.server.id]["self-assign_roles"]["roles"]:
            for serverrole in ctx.message.server.roles:
                if role == serverrole.id:
                    roles.append(serverrole.name)
        return await self.bot.say(roles)

    @bot.command(pass_context=True)
    async def iam(self, ctx, role: discord.Role = None):
        if not self.con.serverconfig[ctx.message.server.id]["self-assign_roles"]["enabled"]:
            return

        user = ctx.message.author
        server = ctx.message.server

        if role not in server.roles:
            return await self.bot.say("That role doesn't exist. Roles are case sensitive. ")

        if role in user.roles:
            return await self.bot.say("You already have that role.")

        if role.id in self.con.serverconfig[ctx.message.server.id]["self-assign_roles"]["roles"]:
            await self.bot.add_roles(user, role)
            print("{} added {} to themselves in {} on {}".format(user.display_name, role.name, ctx.message.channel,
                                                                 ctx.message.server))
            return await self.bot.say("Yay {}! You now have the {} role!".format(user.mention, role.name))
        else:
            return await self.bot.say("That role is not self-assignable.")

    @bot.command(pass_context=True)
    async def addrole(self, ctx, role: discord.Role = None):
        # Add Remove List Help
        if not owner(ctx):
            return await self.bot.reply("You do not have permission to do this command.", delete_after=20)
        else:
            self.con.serverconfig[ctx.message.server.id]["self-assign_roles"]["roles"].append(role.id)
            self.con.updateconfig(self.con.serverconfig)
            return await self.bot.say('Role "{}" added'.format(str(role)))

    @bot.command(pass_context=True)
    async def removerole(self, ctx, role: discord.Role = None):
        if not owner(ctx):
            return await self.bot.reply("You do not have permission to do this command.", delete_after=20)

        if role.id in self.con.serverconfig[ctx.message.server.id]["self-assign_roles"]["roles"]:
            self.con.serverconfig[ctx.message.server.id]["self-assign_roles"]["roles"].remove(role.id)
            self.con.updateconfig(self.con.serverconfig)
            return await self.bot.say('"{}" has been removed from the self-assignable roles.'.format(str(role)))
        else:
            return await self.bot.say("That role was not in the list.")

def setup(Bot):
    Bot.add_cog(selfAssign(Bot))