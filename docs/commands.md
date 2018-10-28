---
title: Command Documentaion
summary: Documentation for all of Roxbot's commands.
authors:
    - Roxanne Gibsin
date: 2018-10-27
---

# Command Documentaion

## Explaination

Before reading this, it is highly recommened you read the [quick start](quickstart.md) guide that will get you upto date with how Roxbot works and how to run her. This is handy if you expect to use commands that will edit Roxbot or Roxbot's guild settings.

## Core Commands
These are the base commands for Roxbot that are a part of the core bot. All of them deal with internal management and are, for the most part, unavalible to average users.

#### ;backup

#### ;blacklist

#### ;changeactivity

#### ;changeavatar

#### ;changenickname

#### ;changestatus

#### ;printsettings

#### ;shutdown

## Cog Commands

### Admin
The Admin cog adds admin commands to Roxbot which should make moderating a Discord server easier.

#### ;ban

#### ;kick

#### ;purge

#### ;slowmode

#### ;unban

#### ;warn

### Custom Commands

#### ;custom

###### ;custom add

###### ;custom edit

###### ;custom list

###### ;custom remove

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

#### ;suck

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

#### ;pride

### Join Leave

#### ;goodbyes

#### ;greets

### NSFW

#### ;e621

#### ;gelbooru

#### ;rule34

---

#### ;nsfw

### Reddit

#### ;aww

#### ;feedme

#### ;feedmevegan

#### ;me_irl

#### ;subreddit

#### ;traa

### Self Assign

#### ;iam

#### ;iamn

#### ;listroles

---

#### ;selfassign

### Trivia

#### ;trivia

###### ;trivia about

###### ;trivia join

###### ;trivia leave

###### ;trivia start

---

###### ;trivia kick

### Util

#### ;avatar

#### ;echo

#### ;emote

#### ;guild

#### ;info

#### ;role

### Voice

#### ;nowplaying

#### ;pause

#### ;play

#### ;queue

#### ;resume

#### ;skip

#### ;stream

#### ;volume

---

#### ;join

#### ;remove

#### ;stop

#### ;voice
