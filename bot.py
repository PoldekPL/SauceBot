#!/usr/bin/env python3

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import asyncio
import random
import time
import sys
import traceback
import os
import os.path
import functools
import re
from urllib import parse

# CONSTANTS
# channel ids

# user ids
admin_id =""

# GLOBAL VARIABLES
token_str = ""      # bot login token
sauce_help = ""     # help message for using SauceNAO
google_help = ""    # help message for Googling

# function to load files
def loadfiles():
    global token_str
    file = open("token", "r")
    token_str = file.read()
    file.close()

    global admin_id
    file2 = open("my_id", "r")
    admin_id = file2.read()
    file2.close()

    global sauce_help
    file3 = open("sauce_help", "r")
    sauce_help = file3.read()
    file3.close()

    global google_help
    file4 = open("google_help", "r")
    google_help = file4.read()
    file4.close()

    return

# helper function for getting formatted time for log
def getLogFormattedTime():
    timestamp_now = time.gmtime()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", timestamp_now)

    return formatted_time

bot = commands.Bot(command_prefix = '!')
bot.remove_command("help")

# load files
loadfiles()

# helper functions to react to messages
async def react_tick(message):
    await bot.add_reaction(message, '✅')

async def react_cross(message):
    await bot.add_reaction(message, '❌')

async def react_cycle(message):
    await bot.add_reaction(message, '♻')

# restart command
@bot.command(aliases = ['reload'], pass_context = True)
async def restart(ctx):
    if ctx.message.author.id == admin_id:
        # log the use of restart command
        print("\n{}: Rebooting due to restart command.\n".format(getLogFormattedTime()))
        await react_cycle(ctx.message)
        # save the id of the message to tick after reboot
        f = open("./restart_msg_id", "w+")
        f.write(ctx.message.id)
        f.write(" ")
        f.write(ctx.message.channel.id)
        f.close()
        # properly shut down
        await bot.logout()
        # restart
        os.execl(os.path.abspath(__file__), "")
    else:
        await react_cross(ctx.message)
        await bot.send_message(ctx.message.channel, "You do not have permissions to restart the bot!")

# bot and server status
@bot.command(pass_context = True)
async def status(ctx):
    pver = sys.version_info
    
    status_embed = discord.Embed(title = "Ready.", colour = 0x3c4b72)
    status_embed.set_thumbnail(url = bot.user.avatar_url)
    status_embed.add_field(name = "discord.py version", value = "%s, running under Python %d.%d.%d" % (discord.__version__, pver[0], pver[1], pver[2]))
    status_embed.set_footer(text = "To read about how to use the SauceBot, use !sauce")

    await bot.send_message(ctx.message.channel, embed = status_embed)

# reload files
@bot.command(aliases = ["loadfiles"], pass_context = True)
async def reloadfiles(ctx):
    if ctx.message.author.id == admin_id:
        loadfiles()
        await react_tick(ctx.message)
    else:
        await bot.send_message(ctx.message.channel, "You do not have permissions to do that!")

# SauceNAO
@bot.command(pass_context = True, aliases = ["s"])
async def sauce(ctx, *, link: str = None):
    global sauce_help

    # if there message body after !sauce command (link string) is empty
    if link == None:
        # if there is a file (or files) attached
        if len(ctx.message.attachments) > 0:
            # iterate over attached files and create saucenao links with their urls
            for a in ctx.message.attachments:
                pic_url = a['url']
                encoded_url = parse.quote_plus(pic_url)
                await bot.send_message(ctx.message.channel, "https://saucenao.com/search.php?url={}".format(encoded_url))
        
        else:
            # no message, no attachments. explain command usage
            await bot.send_message(ctx.message.channel, sauce_help)
        return
    else:
        # there was something after !sauce command, link string is non-empty
        # detect if that's a valid discord message permalink
        if re.fullmatch(r"https://discordapp\.com/channels/\d+/\d+/\d+", link, re.I) != None:
            discord_link = True
        else:
            discord_link = False

    # using discord permalink detection result, either analyze the linked message or directly put given string in saucenao link
    if discord_link == True:
        # if that was a message permalink, extract server, channel and message ids
        ids = re.findall(r"\d+", link, re.I)
        # fetch linked message
        linked_message = await bot.get_message(discord.Object(ids[1]), ids[2])
        # if linked message has file(s) attached
        if len(linked_message.attachments) > 0:
            # iterate over attached files and create saucenao links with their urls
            for a in linked_message.attachments:
                pic_url = a['url']
                encoded_url = parse.quote_plus(pic_url)
                await bot.send_message(ctx.message.channel, "https://saucenao.com/search.php?url={}".format(encoded_url))
        else:
            await bot.send_message(ctx.message.channel, "Linked message does not have attached pictures.")
        return
    else:
        # if that was not a discord message assume it's a permalink to a picture and use that to create saucenao link
        encoded_url = parse.quote_plus(link)
        await bot.send_message(ctx.message.channel, "https://saucenao.com/search.php?url={}".format(encoded_url))

        return

# Google Reverse Image Search
@bot.command(pass_context = True, aliases = ["g"])
async def google(ctx, *, link: str = None):
    global google_help

    # if there message body after !google command (link string) is empty
    if link == None:
        # if there is a file (or files) attached
        if len(ctx.message.attachments) > 0:
            # iterate over attached files and create google links with their urls
            for a in ctx.message.attachments:
                pic_url = a['url']
                encoded_url = parse.quote_plus(pic_url)
                await bot.send_message(ctx.message.channel, "https://www.google.com/searchbyimage?&image_url={}".format(encoded_url))
        
        else:
            # no message, no attachments. explain command usage
            await bot.send_message(ctx.message.channel, google_help)
        return
    else:
        # there was something after !google command, link string is non-empty
        # detect if that's a valid discord message permalink
        if re.fullmatch(r"https://discordapp\.com/channels/\d+/\d+/\d+", link, re.I) != None:
            discord_link = True
        else:
            discord_link = False

    # using discord permalink detection result, either analyze the linked message or directly put given string in google link
    if discord_link == True:
        # if that was a message permalink, extract server, channel and message ids
        ids = re.findall(r"\d+", link, re.I)
        # fetch linked message
        linked_message = await bot.get_message(discord.Object(ids[1]), ids[2])
        # if linked message has file(s) attached
        if len(linked_message.attachments) > 0:
            # iterate over attached files and create google links with their urls
            for a in linked_message.attachments:
                pic_url = a['url']
                encoded_url = parse.quote_plus(pic_url)
                await bot.send_message(ctx.message.channel, "https://www.google.com/searchbyimage?&image_url={}".format(encoded_url))
        else:
            await bot.send_message(ctx.message.channel, "Linked message does not have attached pictures.")
        return
    else:
        # if that was not a discord message assume it's a permalink to a picture and use that to create google link
        encoded_url = parse.quote_plus(link)
        await bot.send_message(ctx.message.channel, "https://www.google.com/searchbyimage?&image_url={}".format(encoded_url))

        return

# command exception handler
@bot.event
async def on_command_error(exception, ctx: discord.ext.commands.Context):
    # if user tried using an unknown command
    if type(exception) == discord.ext.commands.errors.CommandNotFound:
        # do nothing, this bot literally has only a single command for users
        pass

# what to do on successful boot
@bot.event
async def on_ready():
    print("\n###\n[{}]: k. running as {}, discord.py version {}\n###\n".format(getLogFormattedTime(), bot.user.name, discord.__version__))

    # if the bot bot was restarted with a restart message, tick it after the restart
    if os.path.exists("./restart_msg_id"):
        f = open("./restart_msg_id", "r")
        msg_id_str = f.read()
        f.close()

        msg_id_contents = msg_id_str.split(' ')
        msg_id = msg_id_contents[0]
        msg_channel_id = msg_id_contents[1]
        msg_channel = discord.utils.get(list(bot.servers)[0].channels, id=msg_channel_id)

        restart_msg = await bot.get_message(msg_channel, msg_id)
        await bot.remove_reaction(restart_msg, '♻', bot.user)
        await react_tick(restart_msg)

        os.remove("./restart_msg_id")
    
    await bot.change_presence(game=discord.Game(name="!sauce || !google", url=None, type=0), status=None, afk=False)

bot.run(token_str)