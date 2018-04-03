![Banner](http://i.imgur.com/SZIVXEg.png)

[![MIT](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.5%2B-blue.svg?style=flat-square)](https://github.com/RainbowDinoaur/roxbot/)
[![Say Thanks](https://img.shields.io/badge/say-thanks-ff69b4.svg?style=flat-square)](https://saythanks.io/to/Roxxers)

RoxBot, A Discord Bot made by a filthy Mercy Main. Built with love (and discord.py)

## Simple setup

_Coming Soon_

## Command Docs
*Coming soon*

## Changelog

#### v1.6.0
###### New Features
- `waifurate` command can now do husbando and spousu rates as well.
- `pet` command for your headpats needs.
###### Minor Changes
- Logging is now easier internally.
- The subreddit command has logging. Only when it is being directly invoked and not when an inbuilt command is being used.
- Added who the waifu command is dedicated to in the command description.
###### Bug Fixes

#### v1.5.1
##### Hot Fixes
- inviteme is hidden and added an extra warning for people not to use it.
- subreddit command shouldnt break now if you give it a subreddit that is pretty close to an actual sub but isn't one.
- Fixed config errors when leaving and joining servers.

#### v1.5.0
###### New Features
- New Ban, Kick, and Unban commands.
- New Guild and Role Util commands.
- Logging is now a thing. Just limited to what I was using hack code to do in GSSP. Clean code, happy Roxie.ye
- New feedmevegan command for hungry vegan friends.
- inviteme command for quickly creating an invite link for the bot.
- Added new error catching for the GSSP cog in case the Tatsumaki API dies or something.
###### Refactoring
- Brand new way of storing, saving, and interacting with the guild settings. The new system should be better to read, understand, and shouldn't be as broken as the old version. Really only a note for those looking at the source code as all functionality should be the same other than roxbot should no longer require rebooting to have up to date settings.
- Also a new file structure layout so it looks nice.
- Changed the name of the welcome channel to the greets channel externally.
###### Bug Fixes
- Fixed bug where using the ;emoji command on a static emoji would return an empty file.
- Fixed bug where roxbot would not have up to date settings at times.
- Fixed the shutdown and reboot commands so they aren't broken anymore.
- Fixed bugs in the gss cog which caused issues from time to time for no reason.
- Fixed an issue where the check failure error would be picked up before it's sub errors meaning they would never be catched by the error handler.
- Fixed the biggest bugs of Roxbot. Fun and CustomCommands where ordered the wrong way in the cog loader, and the GSSP cog's class being called "GaySoundsShitposting" which is just disgusting.
- Fixed bug where conversion error in iam commands didn't raise an exception.
- Added error handling to when you did the self assign commands without any arguments.

#### v1.4.1
###### Bug Fixes
- Lots of small bug fixes todo with the move over to int ID's and the internal settings being :b:roke.


#### v1.4.0

###### New Stuff!
- A whole trivia game, right in your discords. Using the Open Trivia DB!
- A complete overhaul of the settings cog so that the settings commands no longer suck and should be easier to use.
- Most, if not all, commands now have documentation in the bot on what they do and how to use them.
- Bot may be easier to use. I am unsure though.
- Added error handling that will actually tell people when errors occur instead of being silent.
- NSFW now has a blacklist feature that can be edited by mods and admins. Just basic tag filters.
- **FROGTIPS**

###### Boring Stuff
- Roxbot has been ported over to the 1.0 version of discord.py. Meaning that she will actually be upto date with new discord changes for once. This also means that there is quite a few new features and bug fixes with this version. 
- New fil structure that will be easier to read and know whats going on.
- servers.json is no longer versioned.
- Unhidden all commands so that it should be easier for mods to know the mod commands.

###### Bug Fixes
- emoji command works with animated emoji.
- avatar command works with animated avatars.
- Non-prefix multi word custom commands should work now and should be removable.
- Fixed issues with the warning commands when a warned user wasn't in the server.
- Fixed bug where capitalisation in the subreddit command would return nothing.
- Twitch shilling now doesn't trigger when someone uses spotify thanks to discord.py update. Also the code is a lot nicer now.

#### v1.3.4
###### Performance
- Changed the warning listing command do that it isn't slow.
###### Bug Fixes
- Removing all warnings of a user now removes them from the dictionary. Making them not display in the list even though they don't have any warnings.


#### v1.3.3
###### Hottest of Bug Fixes
- Warn list now actually works for all warnings.
- Slowmode now ignores mods and admins.

#### v1.3.2
###### Bug Fixes
- Fixed logging for gss cog again...

#### v1.3.1
###### Bug Fixes
- Fixed logging for gss cog.

#### v1.3.0
###### New Features
- New Admin Cog with warning and slowmode commands.
- Hug Command like that of suck and spank
- 'Succ' now added as an alias for ;suck
- The GSS cog commands are more efficient
- ;nsfwperms and ;selfieperms can now be repeated to remove the roles.
- NSFW channels can now be added to selectively enable Roxbot's NSFW features.
- New checks for the suck and spank commands so that they too can be disabled on a channel basis.

###### Bug Fixes
- Fixed bug where Custom Commands would ignore the blacklist.
- Fixed issue where custom command outputs were always lowercase
- Fixed some naughty swears that were placeholders for a more civilised response.
- Removed Herobrine

#### v1.2.0
###### New Features
- Added a new cog for the GaySoundsShiposts discord. Just some custom commands needed for modding.

#### v1.1.3
###### Changes
- Changed to traa command to gss and point to the /r/gaysoundsshitposts subreddit

#### v1.1.2
###### Bug Fixes
- Fixed a bug when a user only had the '@everyone' role and used ;info.

#### v1.1.1
###### Bug Fixes
- Print settings outputting too big of a message
- perm roles being overwritten

#### v1.1.0
###### New Features
- Custom commands! With and without prefixes, the bot can output a custom message.
- Admin roles to check for perms

#### v1.0.0
###### Rewrite
The whole bot has been completly rewritten. Its jam packed with new commands, cogs, and functionality. Because of this, I wont be including a full change log. I will fill out the changelog for further versions. But this version should be more stable, have more features, and just be better than before.

#### v0.4.0
###### New Features
- New commands in fun like a reddit scrapper.
- New Utils cog, new commands like avatar, and info

###### Bugs and Fixes
- Admin cog renamed to Settins cog.
- ChangeAvatar updated again to be inline with who avatar deals with avatar images.
- Fixed twitch cog bug that made roxbot crash a lot

Probs more but I forgot honestly

#### v0.3.6
- ChangeAvatar command updated to use a upto date function to download images
- printsetting command created for bot owner to check the serverconfig at the current time

#### v0.3.5
- Changelog created

#### Pre-v0.3.5
- Bot was made. Wasn't great. You can check the commits though for more info.


## Licence
[MIT Licence](https://github.com/RainbowRoxxers/roxbot/blob/master/LICENSE)
