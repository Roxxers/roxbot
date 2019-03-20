# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017-2018 Roxanne Gibson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import random
import argparse

import discord
from discord.ext import commands

from roxbot import http, config, exceptions


class ArgParser(argparse.ArgumentParser):
    """Create Roxbot's own version of ArgumentParser that doesn't exit the program on error."""
    def error(self, message):
        # By passing here, it will just continue in cases where a user inputs an arg that can't be parsed.
        pass


async def danbooru_clone_api_req(channel, base_url, endpoint_url, cache=None, tags="", banned_tags="", sfw=False):
    """Utility function that deals with danbooru clone api interaction.
    It also deals with cache management for these interactions.

    Params
    =======
    channel: discord.Channel
        Channel command has been invoked in
    base_url: str
        Base url of the site
    endpoint_url: str
        Endpoint of images in the API. This is used if the API does not give this in its response.
    cache: dict (optional)
        Post cache. Were channel ID's are keys with values that are lists of identifiable info.
        Cache is handled in this function and will be updated so that other functions can access it.
    tags: str (optional)
        tags to use in the search. Separated by spaces.
    banned_tags: str (optional)
        banned tags to append to the search. Separated by spaces with a - in front to remove them from search results.
    """
    limit = "150"
    is_e621_site = bool("e621" in base_url or "e926" in base_url)

    if is_e621_site:
        banned_tags += " -cub"  # Removes TOS breaking content from the search
        tags = tags + banned_tags
        if len(tags.split()) > 6:
            raise exceptions.UserError("Too many tags given for this site.")
    else:
        banned_tags += " -loli -shota -shotacon -lolicon -cub"  # Removes TOS breaking content from the search
        tags = tags + banned_tags

    page_number = str(random.randrange(20))

    if "konachan" in base_url or is_e621_site:
        page = "&page="
    else:
        page = "&pid="
    url = base_url + tags + '&limit=' + limit + page + page_number

    if isinstance(channel, discord.DMChannel):
        cache_id = channel.id
    else:
        cache_id = channel.guild.id

    # IF ID is not in cache, create cache for ID
    if not cache.get(cache_id, False):
        cache[cache_id] = []

    posts = await http.api_request(url)

    if not posts:
        return None

    post = None
    while posts:
        index = random.randint(0, len(posts)-1)
        post = posts.pop(index)
        if sfw:
            if post["rating"] == "e" or post["rating"] == "q":
                continue
        md5 = post.get("md5") or post.get("hash")
        if md5 not in cache[cache_id]:
            cache[cache_id].append(md5)
            if len(cache[cache_id]) > 10:
                cache[cache_id].pop(0)
            break
        if not posts:
            return None

    url = post.get("file_url")
    if not url:
        url = endpoint_url + "{0[directory]}/{0[image]}".format(post)
    return url


def has_permissions(ctx, **perms):
    """Copy of code from discord.py to work outside of wrappers"""
    ch = ctx.channel
    permissions = ch.permissions_for(ctx.author)

    missing = [perm for perm, value in perms.items() if getattr(permissions, perm, None) != value]

    if not missing:
        return True
    return False

    #raise commands.MissingPermissions(missing)


def has_permissions_or_owner(ctx, **perms):
    if ctx.author.id == config["Roxbot"]["OwnerID"]:
        return True
    return has_permissions(ctx, **perms)
