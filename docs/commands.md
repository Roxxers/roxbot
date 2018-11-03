---
title: Command Documentaion
description: Documentation for all of Roxbot's commands.
authors:
    - Roxanne Gibson
---

# Command Documentaion

If you intend to use any commands requiring permissions, it is highly recommened you read the [quick start](quickstart.md) guide that will get you upto date with how Roxbot works and how to run her.

## How to use the docs

### What is an alias?

An alias is just another way of executing the command. Usually to shorten the command to be easier to type. If `emoji` is an alias of `emote`, using either `emoji` or `emote` will execute `emote`.

### What do I do when a command wants a channel, user, role, etc.?

When the command wants a CHANNEL, USER, MEMBER, or ROLE. This means the ID, name, or mention of that part of Discord. Role, User, and Member mentions start with a '@' and Channel mentions start with a '#'. A Member is the same as a User except a Member is explicitly a User in a Guild.

## Core Commands
These are the base commands for Roxbot that are a part of the core bot. All of them deal with internal management and are, for the most part, unavalible to average users.

### ;backup

!!! warning "Required Permissions"
    This command can only be exectuted by the owner of the Roxbot instance.

Creates a backup of all server's settings manually. This will make a folder in `settings/backups/`. The name of the folder will be outputted when you use the command. Using only this and not the automatic backups is not recommened.

Command Structure:

`;backup`

### ;blacklist

!!! warning "Required Permissions"
    This command can only be exectuted by the owner of the Roxbot instance.

Manage the global blacklist for Roxbot. 

Command Structure:

`;blacklist option *users`

Options:

- `option` - This is whether to add or subtract users from the blacklist. `+` or `add` for add and `-` or `remove` for remove.

- `users` - A name, ID, or mention of a user. This allows multiple users to be mentioned.

Examples:

```py
# Add three users to the blacklist
;blacklist add @ProblemUser1 ProblemUser2#4742 1239274620373
# Remove one user from the blacklist
;blacklist - @GoodUser
```


### ;changeactivity

!!! warning "Required Permissions"
    This command can only be exectuted by the owner of the Roxbot instance.

Changes the activity that Roxbot is doing. This will be added as a game. "none" can be passed to remove an activity from Roxbot.

Command Structure:

`;changeactivity text`

Aliases:

`activity`

Options:

- `text` -  Either text to be added as the "game" or none to remove the activity.

Examples:

```py
# Change activity to "with the command line" so that it displays "Playing with the command line"
;activity "with the command line"
# Stop displaying any activity
;activity none
```

### ;changeavatar

!!! warning "Required Permissions"
    This command can only be exectuted by the owner of the Roxbot instance.

Changes the avatar of the bot account. This cannot be a gif due to Discord limitations.

Command Structure:

`;changeavatar image`

Aliases:

`setavatar`

Options:

- `image` -  This can either be uploaded as an attachment or linked after the command.

Example:
```py
# Change avatar to linked image
;changeavatar https://i.imgur.com/yhRVl9e.png
```

### ;changenickname

!!! warning
    This command cannot be used in private messages.

!!! warning "Required Permissions"
    This command can only be exectuted by the owner of the Roxbot instance.

Changes the nickname of Roxbot in the guild this command is executed in. 

Command Structure:

`;changenickname name`

Aliases:

`nickname`, `nick`

Options:

- `name` - OPTIONAL: If not given, Roxbot's nickname will be reset.

Example:

```py
# Make Roxbot's nickname "Best Bot 2k18"
;nick Best Bot 2k18
# Reset Roxbot's nickname
;nick
```

### ;changestatus

!!! warning "Required Permissions"
    This command can only be exectuted by the owner of the Roxbot instance.

Changes the status of the bot account.

Command Structure:

`;changestatus status`

Aliases:

`status`

Options:

- `status` - There are four different options to choose. `online`, `away`, `dnd` (do not disturb), and `offline`

Examples:

```py
# Set Roxbot to offline
;changestatus offline
# Set Roxbot to online
;changestatus online
```


### ;echo

!!! warning "Required Permissions"
    This command can only be exectuted by the owner of the Roxbot instance.

Echos the given string to a given channel.

Command Structure:

`;echo channel message`

Example:

```py
# Post the message "Hello World" to the channel #general
;echo #general Hello World
```

### ;help

Displays all commands you can execute in that channel. If a command is specifed, it will show the help for that command.

Command Structure:

`;help [command: optional]`

Options:

- `command` - OPTIONAL: If a command is specifed, it will show the help for that command. If this is a command group, it will show the commands in that group and some help. If a subcommand in a group, then the help for that command.

Examples:

```py
# List all commands I can execute in this current channel
;help
# Show help for the "subreddit" command
;help subreddit
# Show help for the "custom" command group
;help custom
# Show help for the "custom add" subcommand
;help custom add
```

### ;invite

Posts [this](https://discordapp.com/oauth2/authorize?client_id=259869304369971200&scope=bot&permissions=871890001) invite. This allows you to invite Roxbot to your own server.

Command Structure:

`;invite`


### ;printsettings

!!! warning "Required Permissions"
    Command requires the user to have the `manage_guild` permission.

!!! warning
    This command cannot be used in private messages.

Prints settings for the cogs in this guild. 

Command Structure:

`;printsettings [cog: optional]`

Aliases:

`printsettingsraw` - Using this will print the raw version of these files.

Options:

- cog - OPTIONAL. If given, this will only show the setting of the cog given. This has to be the name the printsettings command gives.

Examples:

```py
# Print the settings for the guild 
;printsettings
# print settings just for the Admin cog.
;printsettings Admin
```

### ;shutdown

!!! warning "Required Permissions"
    This command can only be exectuted by the owner of the Roxbot instance.

Shutdowns the bot.

Command Structure:

`;shutdown`

## Cog Commands

Cog commands are all of the commands that aren't in the Core Roxbot code. This is anything that sits in the `cogs/` folder;

## Admin
The Admin cog adds admin commands to Roxbot which should make moderating a Discord server easier.


!!! warning
    This whole cog cannot be used in private messages.

### ;ban

!!! warning "Required Permissions"
    Command requires the user **and** Roxbot to have the `ban_users` permission.
    
Bans the mentioned user with the ability to give a reason.

Command Structure:

`;ban USER [reason: optional]`

Options:

- `USER` - A name, ID, or mention of a user.

- `reason` - OPTIONAL. A short reason for the banning.

Examples:

```py
# Ban user BadUser
;ban @BadUser
# Ban user Roxbot for being a meanie
;ban Roxbot "for being a meanie"
```

### ;kick

!!! warning "Required Permissions"
    Command requires the user **and** Roxbot to have the `kick_users` permission.
    
Kicks the mentioned user with the ability to give a reason.

Command Structure:

`;kick USER [reason: optional]`

Options:

- `USER` - A name, ID, or mention of a user.

- `reason` - OPTIONAL. A short reason for the kicking.

Examples:

```py
# Kick user BadUser
;kick @BadUser
# Kick user Roxbot for being a meanie
;kick Roxbot "for being a meanie"
```


### ;purge

!!! warning "Required Permissions"
    Command requires the user **and** Roxbot to have the `manage_messages` permission.
    
Purges the text channel the command is execture in. You can specify a certain user to purge as well.

Command Structure:

`;purge limit [USER: optional]`

Options:

- `limit` - This the the amount of messages Roxbot will take from the chat and pruge. Note: This **does not** mean the amount that will be purged. Limit is the amount of messages Roxbot will look at. If a user is given, it will only delete messages from that user in that list of messages.

- `USER` - A name, ID, or mention of a user. If the user has left the guild, this **has** to be the ID.


Examples:

```py
# Delete 20 messages from the chat
;purge 20
# Take 20 messages, and delete any message in it by user @Spammer
;purge 20 @Spammer
```


### ;slowmode

!!! warning "Required Permissions"
    Command requires the user **and** Roxbot to have the `manage_channels` permission.
    
Puts the channel in slowmode. Users with `manage_channel` or `manage_messages` permissions will not be effected.

Command Structure:

`;slowmode seconds`

Options:

- `seconds` - Has to be between 0 - 120. This will set the timeout a user receives once they send a message in this channel. If 0, Roxbot will disable slowmode.

Examples:

```py
# Set slowmode to 30 seconds
;slowmode 30
# Turn slowmode off
;slowmode 0
```

### ;unban

!!! warning "Required Permissions"
    Command requires the user **and** Roxbot to have the `ban_users` permission.
    
Unbans the mentioned user with the ability to give a reason.

Command Structure:

`;unban user_id [reason: optional]`

Options:

- `user_id` - The ID of a banned user.

- `reason` - OPTIONAL. A short reason for the unbanning.

Examples:

```py
# Unban user with ID 478294672394
;unban 478294672394
```


### ;warn

!!! warning "Required Permissions"
    Group requires the user to have the `kick_users` permission. <small>The logic here is that if a mod can kick a user, they can warn a user too as they are similar in function.</small>

The warn command group allows Discord moderators to warn users and log them within the bot. The command group also supports setting limits to warn mods if a user has been warned over a certain threshold.

#### ;warn add

Adds a warning to a user.

Command Structure:

`;warn add USER [warning: optional]`

Options:

- `USER` - A name, ID, or mention of a user.

- `warning` - OPTIONAL. A reason for the warning. This supports markdown formatting.

Example:

```py
# Add warning to user @Roxbot for being a meanie
;warn add @Roxbot "for being a meanie"
```

#### ;warn list

Lists all warning in this guild or all the warnings for one user.

Command Structure:

`;warn list [USER: optional]`

Options:

- `USER` - OPTIONAL. A name, ID, or mention of a user.

Examples:

```py
# List all warnings in the guild
;warn list
# List all warnings for @Roxbot
;warn list @Roxbot
```

#### ;warn prune

Prunes the warnings of any banned users. You can add a 1 at the end to dryrun the command. This will show you how many would be deleted without deleting them.

Command Structure:

`;warn prune [dryrun: optional]`

Options:

- `dryrun` - Add `1` to the end of the command to do a dryrun of the prune command.

Examples:

```py
# Prune the warnings of banned users in this guild
;warn prune
# Dryrun the prune command to see how many warnings would be removed
;warn prune 1
```

#### ;warn remove

Removes one or all of the warnings for a user.

Command Structure:

`;warn remove USER [index: optional]`

Options:

- `USER` - A name, ID, or mention of a user.

- `index` - OPTIONAL. The index of the single warning you want to remove.

Examples:

```py
# Remove all warmings for Roxbot
;warn remove Roxbot
# Remove warning 2 for Roxbot
;warn remove Roxbot 2
```

#### ;warn set_limit

Sets the limit for how many warnings a user can get before mod's are notified. If 3 is set, on the third warning, mods will be DM'd. If this is set to 0, DM's will be disabled.

Command Structure:

`;warn set_limit number`

Aliases:

`sl`, `setlimit`

Options:

- `number` - A positive integer. Once this number is equal to the number of warnings a user has, the mod who did the latest warning will be dm'd about it. If it is set to 0, this is disabled.

Examples:

```py
# Set the warning limit to 3
;warn sl 3
# Disable warnings
;warn set_limit 0
```

---

## Custom Commands

The Custom Commands cog allows moderators to add custom commands for their Discord server to Roxbot. Allowing custom outputs predefined by the moderators. 

For example, we can set a command to require a prefix and call it "roxbot" and configure an output. Then if a user does `;roxbot` roxbot will output the configured output.

### ;custom

This command group handle settings for the custom commands. 

!!! warning
    This command group cannot be used in private messages.

#### ;custom add

Add a custom command.

!!! warning "Required Permissions"
    Command requires the user to have the `manage_messages` permission.
    
Command Structure:

`;custom add type name *output`

Aliases:

`cc`

Options:

- `type` - There are three types of custom commands.
    - `no_prefix`/`0` - These are custom commands that will trigger without a prefix. Example: a command named `test` will trigger when a user says `test` in chat.
    - `prefix`/`1` - These are custom commands that will trigger with a prefix. Example: a command named `test` will trigger when a user says `;test` in chat.
    - `embed`/`2` - These are prefix commands that will output a rich embed. [You can find out more about rich embeds from Discord's API documentation.](https://discordapp.com/developers/docs/resources/channel#embed-object) Embed types currently support these fields: `title, description, colour, color, url, footer, image, thumbnail`
- `name` - The name of the command. No commands can have the same name.
- `output` - The output of the command. The way you input this is determined by the type.

`no_prefix` and `prefix` types support single outputs and also listing multiple outputs. When the latter is chosen, the output will be a random choice of the multiple outputs.

Examples:

```py
# Add a no_prefix command called "test" with the output "hello world"
;cc add no_prefix test "hello world"
# Add a prefix command called test2 with a randomised output between "the person above me is annoying" and "the person above me is cool :sunglasses:"
;cc add prefix test2 "the person above me is annoying" "the person above me is cool :sunglasses:
# Add an embed command called test3 with a title of "Title" and a description that is a markdown hyperlink to a youtube video, and the colour #deadbf
;cc add embed test3 title "Title" description "[Click here for a rad video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)" colour #deadbf
```

!!! note
    With custom commands, it is important to remember that "" is used to pass any text with spaces as one thing. If the output you want requires the use of these characters, surround your output with """this""" instead.


#### ;custom edit

Edits an already existing custom command. 

!!! note
    You cannot change the type of a command. If you want to change the type, remove the command and re-add it.

!!! warning "Required Permissions"
    Command requires the user to have the `manage_messages` permission.
    
Command Structure:

`;custom edit command_name new_output`

Example:

For more examples of how to setup a custom command, look at the help for the ;custom add command. 

```py
# edit a command called test to output "new output"
;cc edit test "new output"
```

#### ;custom list

Lists all custom commands for this guild.

Command Structure:

`;custom list`

#### ;custom remove

Removed the named custom command.

!!! warning "Required Permissions"
    Command requires the user to have the `manage_messages` permission.

Command Structure:

`;custom remove command`

Example:

```py
# Remove custom command called "test"
;cc remove test
```

---

## Fun

The Fun cog provides many commands just meant to be fun. Full of a lot of misc commands as well that might provide a few laughs or be entertaining.

### ;aesthetics

Converts text to be more ａｅｓｔｈｅｔｉｃ <small>fix-width text</small>

Command Structure:

`;aesthetics text`

Aliases:

`ae`, `aesthetic`

Example:

```py
# Convert "Hello World" to fixed-width text.
;ae Hello World
```

### ;coinflip

Filps a magical digital coin!

Command Structure:

`;coinfilp`

Aliases:

`cf`

### ;frogtips

RETURNS FROG TIPS FOR HOW TO OPERATE YOUR FROG

Command Structure:

`;frogtips`

Aliases:

`ft`, `frog`

### ;hug

Gives headpats to the mentioned user :3

Command Structure:

`;hug USER`

Options:

- `USER` - A name, ID, or mention of a user.

Examples:
```py
# Two ways to give Roxbot hugs.
;hug @Roxbot#4170
;hug Roxbot
```

### ;numberfact

Returns a fact for the positive integer given. A random number is chosen if none is given.

Command Structure:

`;numberfact postive_integer`

Aliases:

`nf`

Example:

```py
# Random fact for the number 35
;nf 35
```

### ;onthisday

Returns a random fact of something that happened today!

Command Structure:

`;onthisday`

Aliases:

`otd`

### ;pet

Gives headpats to the mentioned user :3

Command Structure:

`;pet USER`

Aliases:

`headpat`, `pat`

Options:

- `USER` - A name, ID, or mention of a user.

Examples:
```py
# Two ways to give Roxbot headpats.
;pet @Roxbot#4170
;pet Roxbot
```

### ;roll

Rolls a die using dice expression format. Spaces in the expression are ignored.

Command structure:

`;roll expression`

Aliases:

`die`, `dice`

!!! example "Examples"
    Roll one d10 two times
    
    ![Output](assets/images/outputs/roll1.png)

    Roll two d20s and takes the highest value, then adds 7
    
    ![Output](assets/images/outputs/roll2.png)


An expression can consist of many sub expressions added together and then a multiplier at the end to indicate how many times the expression should be rolled.

Sub expressions can be of many types:
	
- `[number]` - add this number to the total
- `d[sides]`  - roll a dice with that many sides and add it to the total
- `[n]d[sides]` - roll n dice. each of those dice have [sides] number of sides, sum all the dice and add to the total
    - `add r[number]` - reroll any rolls below [number]
    - `add h[number]` - only sum the [number] highest rolls rather than all of them
    - `add l[number]` - only sum the [number] lowest rolls rather than all of them
- `x[number]` - only use at the end. roll the rest of the expression [number] times(max 10)

Credit: TBTerra#5677

### ;roxbotfact

Returns a random fact about Roxbot! Roxbot has her own lore that you can discover through out these facts. Written especially for Roxbot.

Command Structure:

`;roxbotfact`

Aliases:

`rf`, `roxfact`

### ;spank

Spanks the mentioned user :wink:

!!! warning
    This command will only work in channels marked NSFW or DMs.


Command Structure:

`;spank USER`

Options:

- `USER` - A name, ID, or mention of a user.

Examples:
```py
# Two ways to give Roxbot spanks.
;spank @Roxbot#4170
;spank Roxbot
```

### ;suck

Sucks the mentioned user :wink:

!!! warning
    This command will only work in channels marked NSFW or DMs.


Command Structure:

`;suck USER`

Aliases:

`succ`

Options:

- `USER` - A name, ID, or mention of a user.

Examples:
```py
# Two ways to give Roxbot the succ.
;suck @Roxbot#4170
;suck Roxbot
```

### ;waifurate

Rates the mentioned waifu(s). By using the aliases husbandorate or spousurate, it will change how Roxbot addresses those who she has rated. <small>This may allow multiple people to be rated at once :eyes:</small>

Command Structure:

`;waifurate`

Aliases:

Waifu Aliases: 

`wf`, `wr`

Husbando Aliases: 

`husbandorate`, `hr`

Spousu Aliases: 

`spousurate`, `sr`

Options:

- `USER` - A name, ID, or mention of a user.

Example:

```py
# Rate user#9999    
;waifurate @user#9999
```

!!! quote ""
    This command is dedicated to Hannah, who came up with the command. I hope she's out there getting her waifus rated in peace.

### ;xkcd

Grabs the image & metadata of the given xkcd comic. The query can be a comic number, comic title, or latest to get the latest. If not given, Roxbot will return a random comic.

Command Structure:

`;xkcd [query: optional]`

Example:

```py
# Get random comic
;xkcd
# Get comic number 666
;xkcd 666
# Get comic with the title "Silent Hammer"
;xkcd "Silent Hammer"
# Get latest comic
;xkcd latest
```

### ;zalgo

Sends text to the nether and returns it back to you ̭҉̭̭ͭi̭͎̭ṋ̭̀҈̭̭̋ ̭͉̭z̭̩̭a̭̭̽ḽ̦̭g̭̞̭o̭̤̭ ̭̭͑f̭̻̭o̭̭͢r̭̭̀m̭̭ͮ

Command Structure:

`;zalgo text`

Aliases:

`za`

Example:

```py
# Convert "Hello World" to zalgo.
;zalgo Hello World
```

---

## ImageEditor

The ImageEditor cog is a cog with multiple commands to manipulate images provided by the user.

### ;deepfry

Deepfrys the given image

Command structure: 

`;deepfry image`

Aliases: 

`df`

Args:

- image: Optional

    1. If no image is provided, image will be your avatar
    2. Mention a user, their avatar will be the image
    3. Provide a URL, that will be the image
    4. Provide an image via upload, that image will be deepfried


### ;pride

`;pride` is a command group for multiple pride flag filters. Avalible pride filters are: LGBT, Bisexual, Asexual, Pansexual, Transgender, Non Binary, Agender, Gender Queer, Gender Fluid.

Command structure:

`;pride subcommand image`


Args:

- subcommand: One of the following: `lgbt, bisexual, asexual, pansexual, transgender, nonbinary, agender, genderqueer, genderfuild.`

- image: Optional

    1. If no image is provided, image will be your avatar
    2. Mention a user, their avatar will be the image
    3. Provide a URL, that will be the image
    4. Provide an image via upload, that image will be deepfried

!!! note
    If you want there to be more pride flag filters or feel there are some missing, don't be afraid to [submit an issue to the Github repo!](https://github.com/Roxxers/roxbot/issues/new)


#### ;pride agender

Command structure:

`;pride agender image`


#### ;pride asexual

Command structure:

`;pride asexual image`

Aliases:

`ace`

#### ;pride bisexual

Command structure:

`;pride bisexual image`

Aliases:

`bi`

#### ;pride genderfluid

Command structure:

`;pride genderfluid image`

Aliases:

`gf`

#### ;pride genderqueer

Command structure:

`;pride genderqueer image`

Aliases:

`gq`

#### ;pride lgbt

Command structure:

`;pride lgbt image`


#### ;pride nonbinary

Command structure:

`;pride nonbinary image`

Aliases:

`nb`, `enby`

#### ;pride transgender

Command structure:

`;pride transgender image`

Aliases:

`trans`

---

## JoinLeave

JoinLeave is a cog that allows you to create custom welcome and goodbye messages for your Discord server. 

!!! warning
    This whole cog cannot be used in private messages.

### ;goodbyes

Edits settings for the goodbye messages.

!!! warning "Required Permissions"
    Command requires the user to have the `manage_messages` permission.


Command Structure

`;goodbyes option [changes: optional]`

Options

- `enable/disable` - Enable/disables goodbye messages.
- `channel` - Sets the channel for the message to be posted in. If no channel is provided, it will default to the channel the command is executed in.


Example:

```
# Enable goodbye messages, set the channel one called `#logs` using a channel mention.
;goodbyes enable
;goodbyes channel #logs
```

### ;greets

Edits settings for the welcome messages

!!! warning "Required Permissions"
    Command requires the user to have the `manage_messages` permission.


Command Structure:

`;greets option [changes: optional]`

Options:

- `enable/disable` - Enable/disables greet messages.
- `channel` - Sets the channel for the message to be posted in. If no channel is provided, it will default to the channel the command is executed in.
- `message` - Specifies a custom message for the greet messages.

Example:

```py
# Enable greet messages, set the channel to the current one, and set a custom message to be appended.
;greets enable
;greets message "Be sure to read the rules and say hi! :wave:"
;greets channel # if no channel is provided, it will default to the channel the command is executed in.
```


---

## NSFW

The NSFW cog is a collection of commands that post images from popular NSFW sites. 

### ;e621

Posts a random image from [e621](https://e621.net) using the tags you provide. Tags can be anything you would use to search the site normally like author and ratings.

!!! warning
    This command will only work in channels marked NSFW or DMs.


Command Structure:

`;e621 [*tags: optional]`

Examples:

```py
# Post a random image
;e621
# Post a random image with the tag "test"
;e621 test
```

### ;gelbooru

Posts a random image from [gelbooru](https://gelbooru.com) using the tags you provide. Tags can be anything you would use to search the site normally like author and ratings.

!!! warning
    This command will only work in channels marked NSFW or DMs.


Command Structure:

`;gelbooru [*tags: optional]`

Examples:

```py
# Post a random image
;gelbooru
# Post a random image with the tag "test"
;gelbooru test
```

### ;rule34

Posts a random image from [rule34.xxx](https://rule34.xxx/) using the tags you provide. Tags can be anything you would use to search the site normally like author and ratings.

!!! warning
    This command will only work in channels marked NSFW or DMs.

Command Structure:

`;rule34 [*tags: optional]`

Examples:

```py
# Post a random image
;rule34
# Post a random image with the tag "test"
;rule34 test
```

---

### ;nsfw

Edits settings for the nsfw cog and other nsfw commands.

!!! warning "Required Permissions"
    Command requires the user to have the `manage_channels` permission.

!!! warning
    This command cannot be used in private messages.


Options:
	`enable/disable`: Enable/disables nsfw commands.
	`addbadtag/removebadtag`: Add/Removes blacklisted tags so that you can avoid em with the commands.

Example:

```py
# Enabled NSFW commands
;nsfw enable
# Add "test" as a blacklisted tag
;nsfw addbagtag test
# Remove "Roxbot" as a blacklisted tag
;nsfw removebadtag Roxbot
```

---

## Reddit

The Reddit cog is a cog that allows users to get images and videos from their favourite subreddits.

### ;subreddit

Grabs an image or video (jpg, png, gif, gifv, webm, mp4) from the subreddit inputted.

Command Structure:

`;subreddit name_of_subreddit`

Example:

```py
# Get images from /r/pics
;subreddit pics
```

---

!!! info
    The following commands are alias-like commands that function like `;subreddit`, randomly selecting a subreddit in a collection of themed subreddits to get a post from.

### ;aww

Gives you cute pics from reddit

Subreddits: 

`"aww", "redpandas", "lazycats", "rarepuppers", "awwgifs", "adorableart"`

Command Structure:

`;aww`

### ;feedme

Feeds you with food porn.

Subreddits: 

`"foodporn", "food", "DessertPorn", "tonightsdinner", "eatsandwiches", "steak", "burgers", "pizza", "grilledcheese", "PutAnEggOnIt", "sushi"`

Command Structure:

`;feedme`

### ;feedmevegan

Feeds you with vegan food porn.

Subreddits: 

`"veganrecipes", "vegangifrecipes", "veganfoodporn"`

Command Structure:

`;feedmevegan`

### ;me_irl

The full (mostly) me_irl network of subs.

Subreddits: 

`"me_irl", "woof_irl", "meow_irl", "metal_me_irl"`

Command Structure:

`;me_irl`

Aliases:

`meirl`

### ;traa

Gives you the best trans memes for daysssss

Subreddits: 

`"gaysoundsshitposts", "traaaaaaannnnnnnnnns"`

Command Structure:

`;traa`

Aliases:

`gssp`, `gss`, `trans_irl`

---

## SelfAssign

The SelfAssign cog allows guild's to mark roles as 'self assignable'. This allows users to give themselves these roles and to see all the roles marked as 'self assignable'.

!!! warning
    This whole cog cannot be used in private messages.

### ;iam

Self-assign yourself a role. Can only be done one role at a time.

Command Structure:

`;iam role`

Example:

`;iam OverwatchPing`


### ;iamn

Remove a self-assigned role. Can only be done one role at a time.

Command Structure:

`;iamn role`

Example:

`;iamn OverwatchPing`


### ;listroles

List's all roles that can be self-assigned on this server.

Command Structure:

`;listroles`


---

### ;selfassign

Edits settings for self assign cog.

!!! warning "Required Permissions"
    Command requires the user to have the `manage_roles` permission.


Command Structure:

`;sa option [role: optional]`

Aliases:

`sa`

Options:
    enable/disable: Enable/disables the cog.
    add/remove: adds or removes a role that can be self assigned in the server.

Example:
```py
# Turn on self assigned roles and add a role called "ROLE"
;sa enable
;sa add ROLE
```

---

## Trivia

![roxbottrivialogo](assets/images/roxbottriviabanner.png)

Roxbot Trivia is a trivia game in *your* discord server. It's heavily inspired by Tower Unite's Trivia mini-game. Learn how to play Roxbot Trivia [here](trivia.md). More detailed documentation can be found below.


This cog works better if the bot account is in the Roxbot Emoji Server. If it cannot find the emotes it needs, it will default to unicode emoji.

!!! warning
    This whole cog cannot be used in private messages.

!!! info "Disclaimer"
    Roxbot Trivia uses the Open Trivia Database, made and maintained by Pixeltail Games LLC. The OpenTDB is licensed under the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Find out more at [https://opentdb.com/](https://opentdb.com/).

### ;trivia

Command group for the Roxbot Trivia game. All interactions with the game are done through this command.

Command Structure: 

`;trivia subcommand`

Aliases: 

`tr`

#### ;trivia about

Displays help in playing Roxbot Trivia. If nothing/an incorrect subcommand is passed to the trivia command, this command is invoked instead. This outputs something similar to the [About Roxbot Trivia page](trivia.md).

Command Structure:

`;trivia about`

#### ;trivia join

Joins a Trivia game in this channel. The game must be waiting for players to join after a user has executed the `;trivia start` command. You cannot join a game in progress.

Command Structure:

`;trivia join`

#### ;trivia leave

Command to leave the game. When invoked, the user leaves the game and their score is removed from the leaderboard. This can be done at any point of the game.

Command Structure:

`;trivia leave`

#### ;trivia start

Starts a trivia game in the channel the command was invoked in. 

Command Structure: 

`;trivia start [*args: optional]`

Args: 

- `--mobile`/`-m` - Launches the game in a mobile compatible mode. In case rich embeds are not readable, especially for Android users.

- `--solo`/`-s` - Skips waiting for users to join and launches the game immediatly. Useful for users just wanting to play solo.

- `--length`/`-l` - Takes option for the length of the game. Acceptable options are `short` (5 Questions), `medium` (10), and `long` (15).

Examples:

```py
# Start a standard trivia game
;trivia start

# Start a mobile compatible solo game of Roxbot Trivia
;tr start -ms

# Start a solo short game
;tr start --solo --length short
```

#### ;trivia kick

Mod command to kick users out of the game. Useful if a user is AFK because of the timer on answering questions.

!!! warning "Required Permissions"
    Command requires the user to have the `manage_channels` permission.


Command Structure:

`;trivia kick user`

Options:

- `user` - A name, ID, or mention of a user.

Example:

```py
# Kick user called BadTriviaPlayer
;tr kick @BadTriviaPlayer
```

---

## Util

The Util cog is a cog filled with a number of utility commands to help more advanced users of Discord.

### ;avatar

Uploads a downloadable picture of an avatar. 

Command Structure:

`;avatar [user: optional]`

Options:

- `user` - OPTIONAL: A name, ID, or mention of a user. If provided, the command will return the user's avatar, if not, it will provide your own.

Example:

```py
# Get my avatar
;avatar
# Get USER's avatar
;avatar USER#0001
```


### ;emote

Displays infomation (creation date, guild, ID) and an easily downloadable version of the given custom emote.

Command Structure:

`;emote EMOTE`

Aliases:

`emoji`

Options:

- `emote` - Needs to be a valid custom emoji

Example:

```py
# Get infomation of the emoji ":Kappa:"
;emote :Kappa:
```

### ;guild

Gives information (creation date, owner, ID) on the guild this command is executed in.

!!! warning
    This command cannot be used in private messages.

Command Structure:

`;guild`

Aliases:

`server`

### ;info

Provides information (account creation date, ID, roles [if in a guild]) on your or another persons account.

Command Structure:

`;info [USER: optional]`

Aliases:

`user`

Options:

- `USER` - OPTIONAL: A name, ID, or mention of a user.

Examples:

```py
# Get account information for yourself
;info
# Get account information for a user called USER
;info @USER
```

### ;role

Gives information (creation date, colour, ID) on the role given. Can only work if the role is in the guild you execute this command in.

!!! warning
    This command cannot be used in private messages.

Command Structure:

`;role ROLE`

Options:

- `ROLE` - Name, ID, or mention of the role you want the info for. 

Example:

```py
# Get information on the role called Admin
;role Admin
```

---

## Voice

The Voice cog is a cog that adds and manages a fully-functional music bot for Roxbot.

!!! warning
    This whole cog cannot be used in private messages.

### ;join

### ;nowplaying

### ;pause

### ;play

### ;queue

### ;remove

### ;resume

### ;skip

### ;stop

### ;stream

### ;volume

### ;voice
