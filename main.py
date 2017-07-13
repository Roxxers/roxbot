# RoxBot
# Version = 1.1
# Author = Roxxers

##############
# To-do List #
##############

# TODO: On member role assign, welcome member using on_member_update
# TODO: Better help menu- AutoGen using <command>.help
# TODO: WaifuRater - Mention user and RNG a rating
# TODO: Admin tools - For commands already in and things like purge a chat
# TODO: Overwatch stats - Using Overwatch-API lib
# TODO: Move away from using ID's for everthing. Maybe replace list with dict
# TODO: Add check for no channel id when a module is enabled 


import json
import random

import discord
from discord.ext.commands import Bot

bot = Bot(command_prefix=".")
# bot.remove_command("help")
# TODO: Take these from a file, not the program
token = 'MzA4MDc3ODg3MDYyNTQwMjg5.DEW5YA.JfLfU5jPjTFQi0xFI6B_-SKvC54'
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
        },
        "twitch_shilling": {
            "enabled": 0,
            "twitch-channel": "",
            "whitelist": {
                "enabled": 0,
                "list": []
            }
        }
    }
}


def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)


def updateconfig():
    with open('config.json', 'w') as conf_file:
        json.dump(config, conf_file)


def config_errorcheck():
    # Checks for errors in the config files and fixes them automatically
    for server in bot.servers:
        if server.id not in config:
            config[server.id] = config_template["example"]
            updateconfig()
            print("WARNING: The config file for {} was not found. A template has been loaded and saved. All modules are turned off by default.".format(server.name.upper()))
        else:
            for module_setting in config_template["example"]:
                if module_setting not in config[server.id]:
                    config[server.id][module_setting] = config_template["example"][module_setting]
                    updateconfig()
                    print("WARNING: The config file for {} was missing the {} module. This has been fixed with the template version. It is disabled by default.".format(server.name.upper(), module_setting.upper()))


def owner(ctx):
    if owner_id == ctx.message.author.id:
        return True
    else:
        return False


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
    # TODO: First part needs to be moved to wait_until_ready
    config_errorcheck()

    print("Client logged in\n")
    print("Servers I am currently in:")
    for server in bot.servers:
        print(server)
    print("")


@bot.event
async def on_member_update(member_b, member_a):
    # Twitch Shilling Part
    if blacklisted(member_b):
        return

    ts_enabled = config[member_a.server.id]["twitch_shilling"]["enabled"]
    if ts_enabled:
        if not config[member_a.server.id]["twitch_shilling"]["whitelist"]["enabled"] or member_a.id in config[member_a.server.id]["twitch_shilling"]["whitelist"]["list"]:
            if member_a.game:
                if member_a.game.type:
                    channel = discord.Object(config[member_a.server.id]["twitch_shilling"]["twitch-channel"])
                    return await bot.send_message(channel, content=":video_game:** {} is live!** :video_game:\n {}\n{}".format(member_a.name, member_a.game.name, member_a.game.url))


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
    for role in config[ctx.message.server.id]["self-assign_roles"]["roles"]:
        for serverrole in ctx.message.server.roles:
            if role == serverrole.id:
                roles.append(serverrole.name)
    return await bot.say(roles)


##################
# Owner Commands #
##################


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
        return await bot.say("You didn't mention anyone")

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
        return await bot.say('{} user(s) have been added to the blacklist'.format(blacklist_amount))

    elif option in ['-', 'remove']:
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
            return await bot.say('{} user(s) have been removed from the blacklist'.format(blacklist_amount))


@bot.command(pass_context=True)
async def addrole(ctx, role: discord.Role = None):
    # Add Remove List Help
    if not owner(ctx):
        return await bot.reply("You do not have permission to do this command.", delete_after=20)
    else:
        config[ctx.message.server.id]["self-assign_roles"]["roles"].append(role.id)
        updateconfig()
        return await bot.say('Role "{}" added'.format(str(role)))


@bot.command(pass_context=True)
async def removerole(ctx, role: discord.Role = None):
    if not owner(ctx):
        return await bot.reply("You do not have permission to do this command.", delete_after=20)

    if role.id in config[ctx.message.server.id]["self-assign_roles"]["roles"]:
        config[ctx.message.server.id]["self-assign_roles"]["roles"].remove(role.id)
        return await bot.say('"{}" has been removed from the self-assignable roles.'.format(str(role)))
    else:
        return await bot.say("That role was not in the list.")


@bot.command(pass_context=True)
async def enablemodule(ctx, module):
    if not owner(ctx):
        return await bot.reply("You do not have permission to do this command.", delete_after=20)
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
async def set_welcomechannel(ctx, channel: discord.Channel = None):
    if not owner(ctx):
        return await bot.reply("You do not have permission to do this command.", delete_after=20)
    config[ctx.message.server.id]["greets"]["welcome-channel"] = channel.id
    updateconfig()
    return await bot.say("{} has been set as the welcome channel!".format(channel.mention))


@bot.command(pass_context=True)
async def set_goodbyechannel(ctx, channel: discord.Channel = None):
    if not owner(ctx):
        return await bot.reply("You do not have permission to do this command.", delete_after=20)
    config[ctx.message.server.id]["goodbyes"]["goodbye-channel"] = channel.id
    updateconfig()
    return await bot.say("{} has been set as the goodbye channel!".format(channel.mention))


@bot.command(pass_context=True)
async def set_twitchchannel(ctx, channel: discord.Channel = None):
    if not owner(ctx):
        return await bot.reply("You do not have permission to do this command.", delete_after=20)
    config[ctx.message.server.id]["twitch_shilling"]["twitch-channel"] = channel.id
    updateconfig()
    return await bot.say("{} has been set as the twitch shilling channel!".format(channel.mention))


@bot.command(pass_context=True)
async def ts_enablewhitelist(ctx):
    if not owner(ctx):
        return await bot.reply("You do not have permission to do this command.", delete_after=20)
    else:
        if not config[ctx.server.id]["twitch_shilling"]["whitelist"]["enabled"]:
            config[ctx.server.id]["twitch_shilling"]["whitelist"]["enabled"] = 1
            updateconfig()
            return await bot.reply("Whitelist for Twitch shilling has been enabled.")
        else:
            config[ctx.server.id]["twitch_shilling"]["whitelist"]["enabled"] = 0
            updateconfig()
            return await bot.reply("Whitelist for Twitch shilling has been disabled.")


@bot.command(pass_context=True)
async def ts_whitelist(ctx, option, *mentions):
    if not owner(ctx):
        return await bot.reply("You do not have permission to do this command.", delete_after=20)

    whitelist_count = 0

    if not ctx.message.mentions and option != 'list':
        return await bot.reply("You haven't mentioned anyone to whitelist.")

    if option not in ['+', '-', 'add', 'remove', 'list']:
        return await bot.say('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

    if option in ['+', 'add']:
        for user in ctx.message.mentions:
            config[ctx.message.server.id]["twitch_shilling"]["whitelist"]["list"].append(user.id)
            updateconfig()
            whitelist_count += 1
        return await bot.say('{} user(s) have been added to the whitelist'.format(whitelist_count))

    elif option in ['-', 'remove']:
        for user in ctx.message.mentions:
            if user.id in config[ctx.message.server.id]["twitch_shilling"]["whitelist"]["list"]:
                config[ctx.message.server.id]["twitch_shilling"]["whitelist"]["list"].remove(user.id)
                updateconfig()
                whitelist_count += 1
        return await bot.say('{} user(s) have been removed to the whitelist'.format(whitelist_count))

    elif option == 'list':
        return await bot.say(config[ctx.message.server.id]["twitch_shilling"]["whitelist"]["list"])


if __name__ == "__main__":
    config = load_config()
    bot.run(token)
