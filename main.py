##############
# To-do List #
##############

# High Priority #
# TODO: Command Review, look at all commands and flesh them out. Maybe some randomised dialogue so that not every command has only one response. Also self delete timers. Make sure user experience feels nice.
# TODO: Complete rework of the commands. Moving to cog based commands again. Rework the code to be easier and cleaner.

# Mid Priority #
# TODO: Move away from using ID's for everthing. Maybe replace list with dict
# TODO: Admin tools - For commands already in and things like purge a chat
# TODO: On member role assign, welcome member using on_member_update

# Low Priority #
# TODO: Better help menu- AutoGen using <command>.help
# TODO: Overwatch stats - Using Overwatch-API lib
# TODO: Add check for no channel id when a module is enabled


import random
import configparser

import discord
from discord.ext.commands import Bot

from config import config
from cogs import cogs

__version__ = '0.3.0'


settings = configparser.ConfigParser()
settings.read('config/settings.ini')

token = settings["Credentials"]["Token"]
owner_id = settings["RoxBot"]["OwnerID"]
command_prefix = settings["RoxBot"]["CommandPrefix"]

bot = Bot(command_prefix=command_prefix)
con = config.Config(bot)





def mention_commandee(ctx):
    return ctx.message.author


def blacklisted(user):
    with open("config/blacklist.txt", "r") as fp:
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
    # TODO: First part needs to be moved to wait_until_ready
    con.config_errorcheck()
    await bot.change_presence(game=discord.Game(name="v0.3.0_Testing"), status=discord.Status.dnd, afk=False)
    for cog in cogs:
        bot.load_extension(cog)
        print(f"{cog} Cog added")
    print(discord.__version__)
    print("Client logged in\n")
    print("Servers I am currently in:")
    for server in bot.servers:
        print(server)
    print("")


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
    if not con.serverconfig[member.server.id]["greets"]["enabled"]:
        return

    em = discord.Embed(
        title="Welcome to {}!".format(member.server),
        description='Hey {}! Welcome to {}! Be sure to read the rules.'.format(member.mention, member.server),
        colour=0xDEADBF)

    if con.serverconfig[member.server.id]["greets"]["welcome-channel"]:
        channel = discord.Object(con.serverconfig[member.server.id]["greets"]["welcome-channel"])
    else:
        channel = member.server.default_channel

    return await bot.send_message(channel,embed=em)


@bot.event
async def on_member_remove(member):
    if not con.serverconfig[member.server.id]["goodbyes"]["enabled"]:
        return
    else:
        return await bot.send_message(member.server,embed=discord.Embed(
            description="{}#{} has left or been beaned.".format(member.name, member.discriminator), colour=0xDEADBF))





@bot.command(pass_context=True)
async def iam(ctx, role: discord.Role = None, *, user: discord.User = None, server: discord.Server = None):
    if not con.serverconfig[ctx.message.server.id]["self-assign_roles"]["enabled"]:
        return

    user = ctx.message.author
    server = ctx.message.server

    if role not in server.roles:
        return await bot.say("That role doesn't exist. Roles are case sensitive. ")

    if role in user.roles:
        return await bot.say("You already have that role.")

    if role.id in con.serverconfig[ctx.message.server.id]["self-assign_roles"]["roles"]:
        await bot.add_roles(user, role)
        print("{} added {} to themselves in {} on {}".format(user.display_name, role.name, ctx.message.channel,
                                                                 ctx.message.server))
        return await bot.say("Yay {}! You now have the {} role!".format(user.mention, role.name))
    else:
        return await bot.say("That role is not self-assignable.")


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
    for role in con.serverconfig[ctx.message.server.id]["self-assign_roles"]["roles"]:
        for serverrole in ctx.message.server.roles:
            if role == serverrole.id:
                roles.append(serverrole.name)
    return await bot.say(roles)


@bot.command(pass_context=True)
async def waifurate(ctx):
    mentions = ctx.message.mentions
    if not mentions:
        return await bot.reply("You didn't mention anyone for me to rate.", delete_after=10)

    rating = random.randrange(1, 11)
    if rating <= 2:
        emoji = ":sob:"
    elif rating <= 4:
        emoji = ":disappointed:"
    elif rating <= 6:
        emoji = ":thinking:"
    elif rating <= 8:
        emoji = ":blush:"
    elif rating == 9:
        emoji = ":kissing_heart:"
    else:
        emoji = ":heart_eyes:"

    if len(mentions) > 1:
        return await bot.say("Oh poly waifu rating? :smirk: Your combined waifu rating is {}/10. {}".format(rating, emoji))
    else:
        return await bot.say("Oh that's your waifu? I rate them a {}/10. {}".format(rating, emoji))


##################
# Owner Commands #
##################




if __name__ == "__main__":
    bot.run(token)
