---
title: Command Documentaion
summary: Documentation for all of Roxbot's commands.
authors:
    - Roxanne Gibsin
date: 2018-10-27
---

# Command Documentaion

Before reading this, it is highly recommened you read the [quick start](quickstart.md) guide that will get you upto date with how Roxbot works and how to run her. This is handy if you expect to use commands that will edit Roxbot or Roxbot's guild settings.

## Core Commands
These are the base commands for Roxbot that are a part of the core bot. All of them deal with internal management and are, for the most part, unavalible to average users.

#### ;backup

!!! warning
    This command can only be exectuted by the owner of the Roxbot instance.

#### ;blacklist

!!! warning
    This command can only be exectuted by the owner of the Roxbot instance.

#### ;changeactivity

!!! warning
    This command can only be exectuted by the owner of the Roxbot instance.

#### ;changeavatar

!!! warning
    This command can only be exectuted by the owner of the Roxbot instance.

#### ;changenickname

!!! warning
    This command can only be exectuted by the owner of the Roxbot instance.

#### ;changestatus

!!! warning
    This command can only be exectuted by the owner of the Roxbot instance.

#### ;help


#### ;printsettings

!!! warning
    Command requires the user to have the `manage_guild` permission.

!!! warning
    This command cannot be used in private messages.

#### ;shutdown

!!! warning
    This command can only be exectuted by the owner of the Roxbot instance.

## Cog Commands

## Admin
The Admin cog adds admin commands to Roxbot which should make moderating a Discord server easier.

!!! warning
    This whole cog cannot be used in private messages.

### ;ban

!!! warning
    Command requires the user **and** Roxbot to have the `ban_users` permission.

### ;kick

!!! warning
    Command requires the user **and** Roxbot to have the `kick_users` permission.


### ;purge

!!! warning
    Command requires the user **and** Roxbot to have the `manage_messages` permission.


### ;slowmode

!!! warning
    Command requires the user **and** Roxbot to have the `manage_channels` permission.

### ;unban

!!! warning
    Command requires the user **and** Roxbot to have the `ban_users` permission.


### ;warn

!!! warning
    Group requires the user to have the `kick_users` permission. <small>The logic here is that if a mod can kick a user, they can warn a user too as they are similar in function.</small>

__;warn add__

__;warn list__

__;warn prune__

__;warn remove__

__;warn set_limit__

---

## Custom Commands

### ;custom

!!! warning
    This command group cannot be used in private messages.

#### ;custom add

!!! warning
    Command requires the user to have the `manage_messages` permission.

#### ;custom edit

!!! warning
    Command requires the user to have the `manage_messages` permission.

#### ;custom list

#### ;custom remove

!!! warning
    Command requires the user to have the `manage_messages` permission.


---

## Fun

### ;aesthetics

### ;coinflip

### ;frogtips

### ;hug

### ;numberfact

### ;onthisday

### ;pet

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

### ;spank

!!! warning
    This command will only work in channels marked NSFW or DMs.

### ;suck

!!! warning
    This command will only work in channels marked NSFW or DMs.

### ;waifurate

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


#### ;pride asexual

Aliases:

`ace`

#### ;pride bisexual

Aliases:

`bi`

#### ;pride genderfluid

Aliases:

`gf`

#### ;pride genderqueer

Aliases:

`gq`

#### ;pride lgbt


#### ;pride nonbinary


Aliases:

`nb`, `enby`

#### ;pride transgender

Aliases:

`trans`

---

## JoinLeave

JoinLeave is a cog that allows you to create custom welcome and goodbye messages for your Discord server. 

!!! warning
    This whole cog cannot be used in private messages.

### ;goodbyes

Edits settings for the goodbye messages.

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

### ;e621

!!! warning
    This command will only work in channels marked NSFW or DMs.

### ;gelbooru

!!! warning
    This command will only work in channels marked NSFW or DMs.

### ;rule34

!!! warning
    This command will only work in channels marked NSFW or DMs.

---

### ;nsfw

!!! warning
    This command cannot be used in private messages.


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

!!! warning
    Command requires the user to have the `manage_roles` permission.

Edits settings for self assign cog.

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

!!! warning
    Command requires the user to have the `manage_channels` permission.

Mod command to kick users out of the game. Useful if a user is AFK because of the timer on answering questions.

Command Structure:

`;trivia kick user`

Example:

```py
# Kick user called BadTriviaPlayer
;tr kick @BadTriviaPlayer
```

---

## Util

### ;avatar

### ;echo

### ;emote

### ;guild

!!! warning
    This command cannot be used in private messages.


### ;info

### ;invite

### ;role

!!! warning
    This command cannot be used in private messages.

---

## Voice

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
