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

#### ;printsettings

!!! warning
    Command requires the user has the `manage_guild` permission.

!!! warning
    This command cannot be used in private messages.

#### ;shutdown

!!! warning
    This command can only be exectuted by the owner of the Roxbot instance.

## Cog Commands

### Admin
The Admin cog adds admin commands to Roxbot which should make moderating a Discord server easier.

!!! warning
    This whole cog cannot be used in private messages.

#### ;ban

!!! warning
    Command requires the user **and** Roxbot have the `ban_users` permission.

#### ;kick

!!! warning
    Command requires the user **and** Roxbot have the `kick_users` permission.


#### ;purge

!!! warning
    Command requires the user **and** Roxbot have the `manage_messages` permission.


#### ;slowmode

!!! warning
    Command requires the user **and** Roxbot have the `manage_channels` permission.

#### ;unban

!!! warning
    Command requires the user **and** Roxbot have the `ban_users` permission.


#### ;warn

!!! warning
    Group requires the user has the `kick_users` permission. <small>The logic here is that if a mod can kick a user, they can warn a user too as they are similar in function.</small>

__;warn add__

__;warn list__

__;warn prune__

__;warn remove__

__;warn set_limit__

### Custom Commands

#### ;custom

!!! warning
    This command group cannot be used in private messages.

##### Subcommands

__;custom add__

!!! warning
    Command requires the user has the `manage_messages` permission.

__;custom edit__

!!! warning
    Command requires the user has the `manage_messages` permission.

__;custom list__

__;custom remove__

!!! warning
    Command requires the user has the `manage_messages` permission.


### Fun

#### ;aesthetics

#### ;coinflip

#### ;frogtips

#### ;hug

#### ;numberfact

#### ;onthisday

#### ;pet

#### ;roll

Rolls a die using dice expression format. Spaces in the expression are ignored.

**Command structure**

`;roll expression`

**Aliases**

`die`, `dice`

!!! example "Examples"
    Roll one d10 two times
    
    ![Output](assets/images/outputs/roll1.png)

    Roll two d20s and takes the highest value, then adds 7
    
    ![Output](assets/images/outputs/roll2.png)


An expression can consist of many sub expressions added together and then a multiplier at the end to indicate how many times the expression should be rolled.

Sub expressions can be of many types:
	
- `[number] #add this number to the total`
- `d[sides] #roll a dice with that many sides and add it to the total`
- `[n]d[sides] #roll n dice. each of those dice have <sides> number of sides, sum all the dice and add to the total`
    - `add r[number] #reroll any rolls below [number]`
    - `add h[number] #only sum the [number] highest rolls rather than all of them`
    - `add l[number] #only sum the [number] lowest rolls rather than all of them`
- `x[number] #only use at the end. roll the rest of the expression [number] times(max 10)`

Credit: TBTerra#5677

#### ;roxbotfact

#### ;spank

!!! warning
    This command will only work in channels marked NSFW 

#### ;suck

!!! warning
    This command will only work in channels marked NSFW 

#### ;waifurate

#### ;xkcd

Grabs the image & metadata of the given xkcd comic

Example:

    {command_prefix}xkcd 666
    {command_prefix}xkcd Silent Hammer
    {command_prefix}xkcd latest

#### ;zalgo

### Image Editor

#### ;deepfry

Deepfrys the given image

**Command structure**

`;deepfry image`

**Aliases**

`df`

**Args**

image: Optional

1. If no image is provided, image will be your avatar
2. Mention a user, their avatar will be the image
3. Provide a URL, that will be the image
4. Provide an image via upload, that image will be deepfried


#### ;pride

`;pride` is a command group for multiple pride flag filters. Avalible pride filters are: LGBT, Bisexual, Asexual, Pansexual, Transgender, Non Binary, Agender, Gender Queer, Gender Fluid.

**Command structure**

`;pride subcommand image`


**Args**

subcommand: One of the following: `lgbt, bisexual, asexual, pansexual, transgender, nonbinary, agender, genderqueer, genderfuild.`

image: Optional

1. If no image is provided, image will be your avatar
2. Mention a user, their avatar will be the image
3. Provide a URL, that will be the image
4. Provide an image via upload, that image will be deepfried

!!! note
    If you want there to be more pride flag filters or feel there are some missing, don't be afraid to [submit an issue to the Github repo!](https://github.com/Roxxers/roxbot/issues/new)

##### Subcommands

__;pride agender__


__;pride asexual__

**Aliases**

`ace`

__;pride bisexual__


**Aliases**

`bi`

__;pride genderfluid__

**Aliases**

`gf`

__;pride genderqueer__


**Aliases**

`gq`

__;pride lgbt__


__;pride nonbinary__


**Aliases**

`nb`, `enby`

__;pride transgender__

**Aliases**

`trans`

### Join Leave

#### ;goodbyes

!!! warning
    This command cannot be used in private messages.

#### ;greets

!!! warning
    This command cannot be used in private messages.

### NSFW

#### ;e621

!!! warning
    This command will only work in channels marked NSFW or DMs.

#### ;gelbooru

!!! warning
    This command will only work in channels marked NSFW or DMs.

#### ;rule34

!!! warning
    This command will only work in channels marked NSFW or DMs.

---

#### ;nsfw

!!! warning
    This command cannot be used in private messages.


### Reddit

#### ;subreddit

#### ;aww

#### ;feedme

#### ;feedmevegan

#### ;me_irl

#### ;traa

### Self Assign

!!! warning
    This whole cog cannot be used in private messages.

#### ;iam


#### ;iamn



#### ;listroles


---

#### ;selfassign



### Trivia

#### ;trivia

!!! warning
    This command group cannot be used in private messages.


##### Subcommands

__;trivia about__

__;trivia join__

__;trivia leave__

__;trivia start__

__;trivia kick__

### Util

#### ;avatar

#### ;echo

#### ;emote

#### ;guild

!!! warning
    This command cannot be used in private messages.


#### ;info

#### ;invite

#### ;role

!!! warning
    This command cannot be used in private messages.

### Voice

!!! warning
    This whole cog cannot be used in private messages.

#### ;join

#### ;nowplaying

#### ;pause

#### ;play

#### ;queue

#### ;remove

#### ;resume

#### ;skip

#### ;stop

#### ;stream

#### ;volume

#### ;voice
