## 2.2.0


### Changelog

#### Trivia

Trivia has seen a entire overhaul. Users will hopefully notice the improved user experience. Under the hood, Trivia is entirely refactored and is a much easier code base to maintain.

 - Better time/score calculation that should reflect the timer on the question better.
 - Timer added between each question.
 - New reaction method of joining and leaving games while not active (not asking questions).
 - Fixed error that didn't allow new games to be made after an error in the game.

#### Config Storage
Roxbot now uses sqlite for guild settings. This hopefully will lead the more possibilities in developing Roxbot cogs. 

 - Entire guild settings system for cogs has been converted to sqlite from json. This will be done automatically for updating instances.
 
#### Other changes
 - Sanitation added to filenames using the `avatar` command to fix a error for users with illegal characters in their usernames.

---

#### Update Notes

To update, just `git pull` inside of the working directory. Make sure to update dependencies using `python3 -m pip install -Ur requirements.txt` in your venv before you run the bot.


## v2.1.3
 **BEFORE UPDATING, UPDATE ALL DEPENDENCIES USING** `python3 -m pip install -Ur requirements.txt` **IN YOUR VENV**
 - Moved over cogs to use new method introduced in the rewrite of discord.py
 - Changed wording of the role not found errors.

## v2.1.2
 - Fixed bug where Roxbot's delete function would delete itself.
 - Fixed more trivia error handling

## v2.1.1

#### Bug Fixes
- Fixed error that spammed the log but was harmless

## v2.1.0

#### New features
- New 8-ball command due to Roxbot's new found vision of the future. She requested this.
- Trivia has gotten some minor UX and UI changes, mostly to the end leaderboard. This is a precursor to a refactor and rework of the game.

#### Bug fixes and changes
- Fixed some settings commands editing the wrong setting in the backend
- Fixed NSFW commands not handling errors properly
- Twitch cog has been made obsolete and removed from the repo
- Permission checking was really broken. Phew no one noticed :sweat:
- Fixed dumb issue with trivia not picking loading custom emojis
- Fixed bug where `;avatar` didn't return animated pfp correctly
- Fixed reintroduced bug that made emoticons trigger Roxbot's `CommandNotFound` response
- Frogtips' Croaks should not longer return error at end of lifespan

## v2.0.3

- Fixed subreddit command not working with the new log function.

## v2.0.2

- Fixed documentation errors between command and backend settings for ags cog
- Fixed subcommandnotfound errors for command groups in Roxbot
- Fixed internal command logging to not be invoked in DM's
- Fixed some typos in documentation
- Fixed input validating in embed creator for customcommands
- Fixed case issues with section names for printsettings. Should now allow any case and find the correct value.

## v2.0.1

Quickfix time

- Fixed Roxbot init of variables in Voice cog
- Fixed Roxbot being silly and thinking `;greets` not only required text as a variable but also not replying and having incorrect options according to the docs.
- Fixed Roxbot assuming you always want NSFW commands on and accidentally removing the ability to disable them. Lewd.

## v2.0.0
With this update, I wanted Roxbot to reach a mature state. The base of the program should be complete and functional. This update brings a lot of internal changes that should make the development of Roxbot easier for others and myself. It also should make her a lot more stable. Still expect updates with new features, bug fixes, and UX changes. Roxbot is planned to have a 3rd breaking update (v3.0.0) which will be at her Adult state. 2.0 being her Adolescence state, and 1.0 being her Child state. (Guess that makes 0.x her Baby state.)

Roxbot should be easier for users to set up too with this update. I have made full documentation of how she works and how to contribute to the project to make this easier. <small>People better find the easter eggs in the command documentation.</small>

### Big and Breaking Changes
- All settings have been decentralised between servers and cogs. All changes to the settings have been moved to independent commands. This doesn't affect custom commands or warnings.
- Many commands have had overhauls to how they work. Parameters have changed on a number of commands. Please check the documentation on all the commands to familiarise yourself with the new way to input params.
- `is_anal` setting is now obsolete. `;suck` and `;spank` now only work in channels marked NSFW. 
- `perm_roles` setting is now obsolete. All commands will work off Discord's permission system.
- Roxbot will now check for a channel being marked NSFW in Discord rather than using her own internal system. Roxbot's NSFW channels have been made obsolete.

### Regular Updates
#### New Features
- Roxbot Facts! Only the deepest of lore for our dear Roxbot. 
- Custom commands now have two new options. Multiple options can be passed for both prefixed and non-prefixed cc's to allow for custom commands to have random outputs. A new type of prefixed cc has been added, embed, which allows the creation of custom rich embeds.
- `;warn set_limit` will allow guilds to set the number of warnings before Roxbot will DM a mod about them. This is set to zero (disabled) by default.
- Added `;me_irl` subreddit command that outputs images from the me_irl network of subreddits.
- Added more subreddits to the `;aww` command.
- Changed the main name of the `;gss` command to `;traa` while adding ;gss as an alias. Also added `;trans_irl` as an alias.
- `;slowmode` now uses Discord's own slowmode rather than its own system. 
- `;emote` command now has support for Unicode emojis. Will show both svg and png links for twemoji.

#### Minor Changes
- Roxbot will remove all redundant settings (removed roles from self assign, etc.).
- Cogs have a message if they fail to load instead of breaking the entire bot.
- Twitch cog disabled and deprecated. This is a minor change because no one uses it anyway. 
- NSFW commands should have even less chance of dupes with better caching.
- All datetime formatting is now standardised.
- Error messages don't timeout anymore.

#### Bug Fixes
- `;deepfry` command now works all the time.
- Pride filter filenames fixed.
- As many spelling mistakes as possible.
- Music bot in Roxbot has had a majority of its bugginess fixed. Queuing now works all of the time for example.
- If music bot can't find a thumbnail for the nowplaying embed, it will just not have one instead of breaking. 
- Fixed bug where nowplaying embeds would have the wrong queued_by value. 
- NSFW commands fixed.
- Roxbot can now fully function in DM's. Before, she would break. DM's have fewer commands that can be invoked.
- `;subreddit`'s "subscriptable" error has been fixed.
- Common commands that would go over 2000 characters have been paginated to avoid an error with Discord's character limit.

## WARNING 

It is not recommended to use any release before v2.0.0. All previous versions are logged and released as pre-releases and are only here as a historical record for myself. All post-v2.0.0 releases are finished products that are stable.

## v1.8.0
#### New Features
- Image cog with pride flags filters for Pride Month! 🏳️‍🌈 (and deepfrying)
- xkcd command. Can grab a random xkcd, or one with a specified id or title. Or even the latest one.
- New `Z̹̹̀A̹̙̹L̢̹̹Ģ̹̹O̹̹ͨ` command

#### Bug Fixes
- Roll command fixed by Terra
- Fixed an issue where waifurate would still have waifu even with a different gender rate selected. 

#### Misc Changes
- Logging outputs for `aesthetics` and the new command `zaglo` have been changed so that their outputs no longer store what argument was given to the bot. This is to comply with the GDPR and to avoid possibly storing personal information in a channel where the user cannot see and request it's deletion. Instead this has been replaced with the ID of the output message. This should still make the output identifiable for administators.

## v1.7.1
#### New Features
- `warn purge` added to clear warn list of banned users.
#### Bug Fixes
- `warn list` no longer returns error when the list is empty.

## v1.7.0
#### New Features
**Trivia**
- Trivia now has mobile and solo options. Mobile changes the formatting of the questions because rich embeds with Android sucks atm. Solo starts the game instantly and doesn't wait for other users to join.
- Argument passing has changed to accomdate this. To set the length of a game, you need to put `length=short` or other length options after the command. Example `;tr start mobile length=short` would start a short mobile compatible game.
- Trivia can now default on unicode emojis in case the bot isn't in the emoji server.

**NSFW and Reddit**
- NSFW and Reddit commands now have a way to delete the output. This is shown by a delete me reaction that will be added to the output. The person who invoked the command then needs to click that reaction within the 20 second timeout to delete the output.
- NSFW commands now have the same system of preventing dupe outputs

**Misc**
- `onthisday` and `numberfact` commands have been added. Interacting with the numbersapi.com's api.
- `warn` and `purge` can now act on users that have left the guild, if their ID is used as the argument.
- Added more info to the `emoji` command.

#### Misc. Changes
- `avatar` now outputs a png if the image is static.
- EmbedColours are now standardised within RoxBot.
- All of RoxBot's requests are now handled by the http file. All http requests have been moved to aiohttp. 
- requests and lxml have been removed as dependencies of Roxbot.
- `upload` has been disabled for the time being until a way for it to work with aiohttp is found.
- Minor refactoring in places, which involves some directory movement.
- added frogtips cache for quicker frogtips

#### Bug Fixes
- All Voice Bugs have been fixed... for now. Queuing works and some more info has been added to the np output.
- Doubled the amount of times subreddit commands will cycle through possible requests to fix JSONDecode error.
- Fixed error in reddit cog due to changing JSON outputs thanks to new reddit redesign.
- Fixed error when trying to use `warn list` on a user that isn't in the list returning an unhelpful error.
- Fixed `emote` error when using a unicode emote by displaying a helpful error message instead of its non-support.

## v1.6.1
#### Small changes
- `nowplaying` is now more handy and should display more info.
#### Hot Fixes
- Voice has received a number of hot fixes to make sure it works properly.
- Slowmode now doesn't effect mods and admins of that guild.
- Fixed `blacklist` command.
- Fixed backup system because it didn't keep the backup folder there.
- Fixed `unban` command

## v1.6.0
#### New Features
- An entire music bot, right in Roxbot! New voice cog that allows for Roxbot to play audio in voice. A well functional discord music bot 
- `waifurate` command can now do husbando and spousu rates as well.
- `pet` command for your headpats needs.
- `roll` command rewrite by TBTerra#5677. It can now do a lot more complex rolls that makes it actually useful!
- `purge` command added for clearing a chat. Only available to users with the `manage_messages` perms.
- `subreddit` and other subcommands should now have a post cache to improve results and reduce duplicate images appearing.
- Internal settings now have automatic and manual local backups. Manual backups activated by the `backup` command.
- Commands are finally case-insensitive. But not the arguments! So don't think your out of the woods yet, kid.
#### Minor Changes
- Logging is now easier internally.
- Logging output has been improved for the `aesthetics` command.
- The `subreddit` command has logging. Only when it is being directly invoked and not when an inbuilt command is being used.
- Added who the `waifurate` command is dedicated to in the command description.
- Added more helpful error handling for `MissingRequiredArgument`, `BadArgument`, `MissingPermissions`, and `BotMissingPermissions` errors.
- Removed pointless second error with iam commands due to improvement to error handling.
- Reddit cog got some lovely refactoring, code should be more efficient now and speeds should be better. Had some weird bugs with loops.
- `subreddit` and other subcommands now will provide author credit.
#### Bug Fixes
- ";-;" and other similar text emoticons now no longer raise the CommandNotFound error.
- `changenickname` has been fixed. Forgot to port some stuff over in there.
- Fixed `guild` command because that was really messed up and wasn't at all helpful.
- PM's don't flag a million errors now due a fix of the `on_message` event in custom commands.

## v1.5.1
#### Hot Fixes
- inviteme is hidden and added an extra warning for people not to use it.
- subreddit command shouldnt break now if you give it a subreddit that is pretty close to an actual sub but isn't one.
- Fixed config errors when leaving and joining servers.

## v1.5.0
#### New Features
- New Ban, Kick, and Unban commands.
- New Guild and Role Util commands.
- Logging is now a thing. Just limited to what I was using hack code to do in GSSP. Clean code, happy Roxie.ye
- New feedmevegan command for hungry vegan friends.
- inviteme command for quickly creating an invite link for the bot.
- Added new error catching for the GSSP cog in case the Tatsumaki API dies or something.
#### Refactoring
- Brand new way of storing, saving, and interacting with the guild settings. The new system should be better to read, understand, and shouldn't be as broken as the old version. Really only a note for those looking at the source code as all functionality should be the same other than roxbot should no longer require rebooting to have up to date settings.
- Also a new file structure layout so it looks nice.
- Changed the name of the welcome channel to the greets channel externally.
#### Bug Fixes
- Fixed bug where using the ;emoji command on a static emoji would return an empty file.
- Fixed bug where roxbot would not have up to date settings at times.
- Fixed the shutdown and reboot commands so they aren't broken anymore.
- Fixed bugs in the gss cog which caused issues from time to time for no reason.
- Fixed an issue where the check failure error would be picked up before it's sub errors meaning they would never be catched by the error handler.
- Fixed the biggest bugs of Roxbot. Fun and CustomCommands where ordered the wrong way in the cog loader, and the GSSP cog's class being called "GaySoundsShitposting" which is just disgusting.
- Fixed bug where conversion error in iam commands didn't raise an exception.
- Added error handling to when you did the self assign commands without any arguments.

## v1.4.1
#### Bug Fixes
- Lots of small bug fixes todo with the move over to int ID's and the internal settings being :b:roke.


## v1.4.0

#### New Stuff!
- A whole trivia game, right in your discords. Using the Open Trivia DB!
- A complete overhaul of the settings cog so that the settings commands no longer suck and should be easier to use.
- Most, if not all, commands now have documentation in the bot on what they do and how to use them.
- Bot may be easier to use. I am unsure though.
- Added error handling that will actually tell people when errors occur instead of being silent.
- NSFW now has a blacklist feature that can be edited by mods and admins. Just basic tag filters.
- **FROGTIPS**

#### Boring Stuff
- Roxbot has been ported over to the 1.0 version of discord.py. Meaning that she will actually be upto date with new discord changes for once. This also means that there is quite a few new features and bug fixes with this version. 
- New fil structure that will be easier to read and know whats going on.
- servers.json is no longer versioned.
- Unhidden all commands so that it should be easier for mods to know the mod commands.

#### Bug Fixes
- emoji command works with animated emoji.
- avatar command works with animated avatars.
- Non-prefix multi word custom commands should work now and should be removable.
- Fixed issues with the warning commands when a warned user wasn't in the server.
- Fixed bug where capitalisation in the subreddit command would return nothing.
- Twitch shilling now doesn't trigger when someone uses spotify thanks to discord.py update. Also the code is a lot nicer now.

## v1.3.4
#### Performance
- Changed the warning listing command do that it isn't slow.
#### Bug Fixes
- Removing all warnings of a user now removes them from the dictionary. Making them not display in the list even though they don't have any warnings.

## v1.3.3
#### Hottest of Bug Fixes
- Warn list now actually works for all warnings.
- Slowmode now ignores mods and admins.

## v1.3.2
#### Bug Fixes
- Fixed logging for gss cog again...

## v1.3.1
#### Bug Fixes
- Fixed logging for gss cog.

## v1.3.0
#### New Features
- New Admin Cog with warning and slowmode commands.
- Hug Command like that of suck and spank
- 'Succ' now added as an alias for ;suck
- The GSS cog commands are more efficient
- ;nsfwperms and ;selfieperms can now be repeated to remove the roles.
- NSFW channels can now be added to selectively enable Roxbot's NSFW features.
- New checks for the suck and spank commands so that they too can be disabled on a channel basis.

#### Bug Fixes
- Fixed bug where Custom Commands would ignore the blacklist.
- Fixed issue where custom command outputs were always lowercase
- Fixed some naughty swears that were placeholders for a more civilised response.
- Removed Herobrine

## v1.2.0
#### New Features
- Added a new cog for the GaySoundsShiposts discord. Just some custom commands needed for modding.

## v1.1.3
#### Changes
- Changed to traa command to gss and point to the /r/gaysoundsshitposts subreddit

## v1.1.2
#### Bug Fixes
- Fixed a bug when a user only had the '@everyone' role and used ;info.

## v1.1.1
#### Bug Fixes
- Print settings outputting too big of a message
- perm roles being overwritten

## v1.1.0
#### New Features
- Custom commands! With and without prefixes, the bot can output a custom message.
- Admin roles to check for perms

## v1.0.0
#### Rewrite
The whole bot has been completely rewritten. Its jam packed with new commands, cogs, and functionality. Because of this, I wont be including a full change log. I will fill out the changelog for further versions. But this version should be more stable, have more features, and just be better than before.

## v0.4.0
#### New Features
- New commands in fun like a reddit scrapper.
- New Utils cog, new commands like avatar, and info

#### Bugs and Fixes
- Admin cog renamed to Settings cog.
- ChangeAvatar updated again to be inline with who avatar deals with avatar images.
- Fixed twitch cog bug that made roxbot crash a lot

Probs more but I forgot honestly

## v0.3.6
- ChangeAvatar command updated to use a upto date function to download images
- printsetting command created for bot owner to check the serverconfig at the current time

## v0.3.5
- Changelog created

## Pre-v0.3.5
- Bot was made. Wasn't great. You can check the commits though for more info.
