# RoxBot
# Version = 0.1
# Author = Roxxers

##############
# To-do List #
##############

# TODO: On member role assign, welcome member using on_member_update
# TODO: Better help menu- AutoGen using <command>.help
# TODO: WaifuRater - Mention user and RNG a rating
# TODO: Admin tools - For commands already in and things like purge a chat
# TODO: Overwatch stats - Using Overwatch-API lib

import json
import random

import discord
from discord.ext.commands import Bot

bot = Bot(command_prefix=".")
#bot.remove_command("help")
token = ''
token_roxbot = ""
owner_id = "142735312626515979"

config_template = {
    "example": {
        "greets": {
            "enabled": 0,
            "welcome-channel": "",
            "member-role": ""
        },
        "goodbyes": {
            "enabled": 0,
            "goodbye-channel": ""
        },
        "self-assign_roles": {
            "enabled": 0,
            "roles": []
        }
    }
}


def owner(ctx):
    if owner_id == ctx.author.id:
        return True
    else:
        return False


def updateconfig():
    with open('config.json', 'w') as conf_file:
        json.dump(config, conf_file)


def mention_commandee(ctx):
    return ctx.message.author


def blacklisted(user):
    with open("blacklist.txt", "r") as fp:
        for line in fp.readlines():
            if user.id+"\n" == line:
                return True
        return False


def dice_roll(num):
    if num == 100:
        step = 10
    else:
        step = 1
    return random.randrange(step, num+1, step)


@bot.event
async def on_ready():
    print("Client logged in\n\n")
    print("Servers I am currently in:\n")
    for server in bot.servers:
        print(server)

@bot.event
async def on_member_update(before, after):
    if True:
        return
    for role in before.roles:
        print(role.name)
    for role in after.roles:
        print(role.name)


@bot.event
async def on_message(message):
    if blacklisted(message.author):
        return
    else:
        return await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    """
    Greets users when they join a server. 
    
    :param member: 
    :return: 
    """
    if not config[member.server.id]["greets"]["enabled"]:
        return

    em = discord.Embed(
        title="Welcome to {}!".format(member.server),
        description='Hey {}! Welcome to {}! Be sure to read the rules.'.format(member.mention, member.server),
        colour=0xDEADBF)

    if config[member.server.id]["greets"]["welcome-channel"]:
        channel = discord.Object(config[member.server.id]["greets"]["welcome-channel"])
    else:
        channel = member.server.default_channel

    return await bot.send_message(channel,embed=em)


@bot.event
async def on_member_remove(member):
    if not config[member.server.id]["goodbyes"]["enabled"]:
        return
    else:
        return await bot.send_message(member.server,embed=discord.Embed(
            description="{}#{} has left or been beaned.".format(member.name, member.discriminator), colour=0xDEADBF))


@bot.event
async def on_server_join(server):
    config[server.id] = config_template["example"]
    updateconfig()


@bot.event
async def on_server_remove(server):
    config.pop(server.id)
    updateconfig()

@bot.command(pass_context=True)
async def iam(ctx, role: discord.Role = None, *, user: discord.User = None, server: discord.Server = None):

    if not config[ctx.message.server.id]["self-assign_roles"]["enabled"]:
        return

    user = ctx.message.author
    server = ctx.message.server

    if role not in server.roles:
        return await bot.say("That role doesn't exist. Roles are case sensitive. ")

    if role in user.roles:
        return await bot.say("You already have that role.")

    if role.id in config[ctx.message.server.id]["self-assign_roles"]["roles"]:
        await bot.add_roles(user, role)
        print("{} added {} to themselves in {} on {}".format(user.display_name, role.name, ctx.message.channel,
                                                                 ctx.message.server))
        return await bot.say("Yay {}! You now have the {} role!".format(user.mention, role.name))
    else:
        return await bot.say("That role is not self-assignable.")


"""@bot.command(pass_context=True)
async def help(ctx):
    return await bot.say("Not that")"""


@bot.command(pass_context=True)
async def blacklist(ctx, option, *mentions):
    """
    Usage:
        .blacklist [ + | - | add | remove ] @UserName [@UserName2 ...]

    Add or remove users to the blacklist.
    Blacklisted users are forbidden from using bot commands.
    Only the bot owner can use this command
    """
    if not owner(ctx):
        return await bot.reply("You do not have permission to do this command.", delete_after=20)
    blacklist_amount = 0
    mentions = ctx.message.mentions

    if not mentions:
        bot.say("You didn't mention anyone")

    if option not in ['+', '-', 'add', 'remove']:
        return await bot.say('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

    for user in mentions:
        if user.id == owner_id:
            print("[Commands:Blacklist] The owner cannot be blacklisted.")
            await bot.say("The owner cannot be blacklisted.")
            mentions.remove(user)

    if option in ['+', 'add']:
        with open("blacklist.txt", "r") as fp:
            for user in mentions:
                for line in fp.readlines():
                    if user.id+"\n" in line:
                        mentions.remove(user)

        with open("blacklist.txt","a+") as fp:
            lines = fp.readlines()
            for user in mentions:
                if user.id not in lines:
                    fp.write("{}\n".format(user.id))
                    blacklist_amount += 1
        return await bot.say('{} users have been added to the blacklist'.format(blacklist_amount))

    else:
        with open("blacklist.txt","r") as fp:
            lines = fp.readlines()
        with open("blacklist.txt","w") as fp:
            for user in mentions:
                for line in lines:
                    if user.id+"\n" != line:
                        fp.write(line)
                    else:
                        fp.write("")
                        blacklist_amount += 1
            return await bot.say('{} users have been removed from the blacklist'.format(blacklist_amount))


@bot.command(pass_context=True, enabled=False)
async def dice(ctx, num, *, user: discord.User = None):
    # TODO: Change to ndx format
    die = ("4","6","8","10","12","20","100")
    if num not in die:
        if num == "help":
            return await bot.say("!dice - This command random roles a dice. The die I support are (4, 6, 8, 10, 12, 20, 100) like the ones used in Table Top games.")
        else:
            return await bot.say("That is not a dice I know. Try !dice help for help!")
    user = mention_commandee(ctx)
    roll = dice_roll(int(num))
    return await bot.say("You rolled a {}, {}".format(roll,user.mention))

""""@bot.command(pass_context=True)
async def cat(self,ctx):
    from PIL import Image
    images = [None] * 3
    images[0] = Image.open("1.png")
    images[1] = Image.open("2.png")
    images[2] = Image.open("3.png")
    do = 3
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGBA', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save('test.png')
    with Image.open("test.png") as fp:
        await self.bot.send_file(ctx.message.channel,"test.png")
"""

@bot.command(pass_context=True)
async def suck(ctx, user: discord.User = None):
    if user is None:
        try:
            user = ctx.message.mentions[0]
        except:
            return await bot.say("You didn't mention someone for me to suck")
    return await bot.say(":eggplant: :sweat_drops: :tongue: {}".format(user.mention))


@bot.command(enabled=False)
async def printcommands():
    for command in bot.commands:
        print(command)
    return await bot.say("Done.")


@bot.command(pass_context=True)
async def listroles(ctx):
    roles = []
    for role in config[ctx.message.server.id]["self-assign_roles"]["roles"]:
        for serverrole in ctx.message.server.roles:
            if role == serverrole.id:
                roles.append(serverrole.name)
    return await bot.say(roles)


#################
# Owner Commands#
#################


@bot.command(pass_context=True)
async def addrole(ctx, role: discord.Role = None):
    # Add Remove List Help
    if not owner:
        return
    else:
        config[ctx.message.server.id]["self-assign_roles"]["roles"].append(role.id)
        updateconfig()
        return await bot.say('Role "{}" added'.format(str(role)))


@bot.command(pass_context=True)
async def removerole(ctx, role: discord.Role = None):
    if not owner:
        return

    count = 0
    for sa_role in config[ctx.message.server.id]["self-assign_roles"]["roles"]:
        if sa_role == role.id:
            config[ctx.message.server.id]["self-assign_roles"]["roles"].pop(count)
            updateconfig()
            return await bot.say('"{}" has been removed from the self-assignable roles.'.format(str(role)))
        else:
            count += 1
    return await bot.say("That role was not in the list.")


@bot.command(pass_context=True)
async def enablemodule(ctx, module):
    if not owner:
        return await bot.say("You ain't the owner, normie get out!!! REEE!")
    else:
        if module in config[ctx.message.server.id]:
            if not config[ctx.message.server.id][module]["enabled"]:
                config[ctx.message.server.id][module]["enabled"] = 1
                updateconfig()
                return await bot.say("'{}' was enabled!".format(module))
            else:
                config[ctx.message.server.id][module]["enabled"] = 0
                updateconfig()
                return await bot.say("'{}' was disabled :cry:".format(module))
        else:
            return await bot.say("That module dont exist fam. You made the thing")


@bot.command(pass_context=True)
async def welcomechannel(ctx, channel: discord.Channel = None):
    config[ctx.message.server.id]["greets"]["welcome-channel"] = channel.id
    updateconfig()
    return await bot.say("{} has been set as the welcome channel!".format(channel.mention))


@bot.command(pass_context=True)
async def goodbyechannel(ctx, channel: discord.Channel = None):
    config[ctx.message.server.id]["goodbyes"]["goodbye-channel"] = channel.id
    updateconfig()
    return await bot.say("{} has been set as the goodbye channel!".format(channel.mention))


if __name__ == "__main__":

    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    bot.run(token)
