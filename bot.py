#!/usr/bin/env python3

import discord
from discord.ext import commands
import asyncio
import random
import time
import sys
import traceback
import os
import os.path
import subprocess
import functools
import re
from urllib import parse

# CONSTANTS
# channel ids

# user ids
admin_id =""

# GLOBAL VARIABLES
token_str = ""              # bot login token
sauce_help = ""             # help message for using SauceNAO
google_help = ""            # help message for Googling

batch_users_sauce = []      # list of users currently in sauce batch mode
batch_users_google = []     # list of users currently in google batch mode

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

def analyzeMessage(message: discord.Message, contents: str):
    #NOTE: I know that using strings as return values is rather lazy, but it's not meant to be a *high performance* bot

    # if message body is empty
    if contents == None:
        # if there is a file (or files) attached
        if len(message.attachments) > 0:
            return "file"
        else:
            # no message, no attachments.
            return None
    else:
        # message body after command is non-empty
        # does the user want to start batch mode?
        if contents == "start":
            return "batch start"
        # or maybe he wants to stop it?
        elif contents == "stop":
            return "batch stop"
        # if it's not about the batch mode, detect if that's a valid discord message permalink
        elif re.fullmatch(r"https://discordapp\.com/channels/\d+/\d+/\d+", contents, re.I) != None:
            return "discord link"
        # in the end, assume that's just a link to a picture. it's user's responsibility to make sure it's valid
        else:
            return "link"

def getAttachmentURLs(message: discord.Message):
    urls = []

    # iterate over attached files and get their urls
    for a in message.attachments:
        urls.append(a['url'])

    return urls

# function name may not be creative, but it is true
async def commonFunction(ctx: discord.ext.commands.Context, text: str, command: str):
    global sauce_help
    global google_help
    global batch_users_sauce
    global batch_users_google

    if command == "sauce":
        help_str = sauce_help
        batch_users = batch_users_sauce
        link_first_half = "https://saucenao.com/search.php?url="
        verb = "find sauce for"
    elif command == "google":
        help_str = google_help
        batch_users = batch_users_google
        link_first_half = "https://www.google.com/searchbyimage?&image_url="
        verb = "google"

    # analyze the message to decide what's the user's intent
    result = analyzeMessage(ctx.message, text)

    if result == None:
        await bot.send_message(ctx.message.channel, help_str)

    elif result == "file":
        # get urls of attached file(s)
        urls = getAttachmentURLs(ctx.message)
        # iterate over urls and create percent encoded links with them
        for u in urls:
            await bot.send_message(ctx.message.channel, "{}{}".format(link_first_half, parse.quote_plus(u)))

    elif result == "link":
        await bot.send_message(ctx.message.channel, "{}{}".format(link_first_half, parse.quote_plus(text)))

    elif result == "discord link":
        # so that was a message permalink, now extract server, channel and message ids
        ids = re.findall(r"\d+", text, re.I)
        # fetch linked message
        linked_message = await bot.get_message(discord.Object(ids[1]), ids[2])
        # get url(s) of file(s) attached to linked message
        urls = getAttachmentURLs(linked_message)
        # if linked message had file(s) attached
        if len(urls) > 0:
            # iterate over attached files and create links with their urls
            for u in urls:
                await bot.send_message(ctx.message.channel, "{}{}".format(link_first_half, parse.quote_plus(u)))
        else:
            await bot.send_message(ctx.message.channel, "Linked message does not have attached pictures.")

    elif result == "batch start":
        if ctx.message.author.id not in batch_users:
            batch_users.append(ctx.message.author.id)
            await bot.send_message(ctx.message.channel, "{}, you're now in *batch mode*. To {} pictures just attach them to your messages. To leave batch mode, use `!{} stop`.".format(ctx.message.author.mention, verb, command))
        else:
            await bot.send_message(ctx.message.channel, "{}, you're already in batch mode, now either post images to {} or leave batch mode with `!{} stop`!".format(ctx.message.author.mention, verb, command))
    
    elif result == "batch stop":
        if ctx.message.author.id in batch_users:
            batch_users.remove(ctx.message.author.id)
            await bot.send_message(ctx.message.channel, "{}, you've left batch mode. To reenable it, use `!{} start`.".format(ctx.message.author.mention, command))
        else:
            await bot.send_message(ctx.message.channel, "{}, you're not in batch mode! To enable it, use `!{} start`!".format(ctx.message.author.mention, command))

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

# bot status
@bot.command(pass_context = True)
async def status(ctx):
    pver = sys.version_info
    
    status_embed = discord.Embed(title = "Ready.", colour = 0x3c4b72)
    status_embed.set_thumbnail(url = bot.user.avatar_url)
    status_embed.add_field(name = "discord.py version", value = "%s, running under Python %d.%d.%d" % (discord.__version__, pver[0], pver[1], pver[2]))
    status_embed.set_footer(text = "To read about how to use the SauceBot, use !sauce or !google")

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
async def sauce(ctx, *, text: str = None):
    await commonFunction(ctx, text, "sauce")

# Google Reverse Image Search
@bot.command(pass_context = True, aliases = ["g"])
async def google(ctx, *, text: str = None):
    await commonFunction(ctx, text, "google")

# universal on_message function
@bot.event
async def on_message(message: discord.Message):
    global batch_users_sauce
    global batch_users_google

    if message.author == bot.user:
        return      # don't reply to yourself
    
    if message.content.find("start") != -1 or message.content.find("stop") != -1:
        # don't do anything if user wants to leave batch mode or enable it for other service
        await bot.process_commands(message)
        return

    # if given user has sauce batch mode enabled, constantly find source for pictures he's posting
    if message.author.id in batch_users_sauce:
        urls = getAttachmentURLs(message)
        if len(urls) > 0:
            for u in urls:
                await bot.send_message(message.channel, "https://saucenao.com/search.php?url={}".format(parse.quote_plus(u)))
        else:
            await bot.send_message(message.channel, "{}, you're in batch mode. Please post pictures to find sauce for. To leave batch mode, use `!sauce stop`!".format(message.author.mention))

    # if given user has google batch mode enabled, constantly google pictures he's posting
    if message.author.id in batch_users_google:
        urls = getAttachmentURLs(message)
        if len(urls) > 0:
            for u in urls:
                await bot.send_message(message.channel, "https://www.google.com/searchbyimage?&image_url={}".format(parse.quote_plus(u)))
        else:
            await bot.send_message(message.channel, "{}, you're in batch mode. Please post pictures to google. To leave batch mode, use `!google stop`!".format(message.author.mention))

    await bot.process_commands(message)

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

def restartHandler():
    # test for internet connection before restarting the bot
    # for good measure, test two different IP addresses
    while subprocess.run(args = ['ping', '-c 1', '8.8.8.8']).returncode != 0 and subprocess.run(args = ['ping', '-c 1', '1.1.1.1']).returncode != 0:
        time.sleep(5)

    os.execl(os.path.abspath(__file__), "")

try:
    bot.run(token_str)
except:
    # in case of any error, restart the bot
    restartHandler()