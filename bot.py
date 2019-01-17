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
import pickle
from urllib import parse

# CONSTANTS
current_path = sys.path[0]

# GLOBAL VARIABLES
token_str = ""              # bot login token
sauce_help = ""             # help message

batch_data = {}             # batch mode data about who, where and what services

# FUNCTIONS
# function to load files
def loadfiles():
    global current_path

    global token_str
    file = open(current_path + "/token", "r")
    token_str = file.read()
    file.close()

    global sauce_help
    file2 = open(current_path + "/sauce_help", "r")
    sauce_help = file2.read()
    file2.close()

    return

# function to ananlyze the command given by the user
def analyzeCommand(message: discord.Message, contents: str):
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
        # did usex expicitly ask for help?
        if contents == "help":
            return "help"
        # detect if that's a valid discord message permalink
        if re.fullmatch(r"https://discordapp\.com/channels/\d+/\d+/\d+", contents, re.I) != None:
            return "discord link"
        # in the end, assume that's just a link to a picture. it's user's responsibility to make sure it's valid
        else:
            return "link"

# function to extract urls of attachments from message
def getAttachmentURLs(message: discord.Message):
    urls = []

    # iterate over attached files and get their urls
    for a in message.attachments:
        urls.append(a['url'])

    return urls

# helper function for getting formatted time for log
def getLogFormattedTime():
    timestamp_now = time.gmtime()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", timestamp_now)

    return formatted_time

# function to return a string with all available search engines used
def allSources(url: str):
    return "{}\n{}\n{}\n{}\n{}".format(sauceLink(url), googleLink(url), tineyeLink(url), iqdbLink(url), yandexLink(url))

def sauceLink(url: str):
    return "SauceNAO: https://saucenao.com/search.php?url={}".format(parse.quote_plus(url))

def googleLink(url: str):
    return "Google: https://www.google.com/searchbyimage?&image_url={}".format(parse.quote_plus(url))

def tineyeLink(url: str):
    return "TinEye: https://www.tineye.com/search?url={}".format(parse.quote_plus(url))

def iqdbLink(url: str):
    return "IQDB: https://iqdb.org/?url={}".format(parse.quote_plus(url))

def yandexLink(url: str):
    return "Yandex: https://yandex.com/images/search?url={}&rpt=imageview".format(parse.quote_plus(url))

# function to ensure proper restart of the bot in case of irrecoverable error
def restartHandler():
    # test for internet connection before restarting the bot
    # for good measure, test two different IP addresses
    while subprocess.run(args = ['ping', '-c', '1', '8.8.8.8'], stdout = subprocess.DEVNULL).returncode != 0 and subprocess.run(args = ['ping', '-c', '1', '1.1.1.1'], stdout = subprocess.DEVNULL).returncode != 0:
        time.sleep(3)

    print("[{}]: Had to restart with restartHandler".format(getLogFormattedTime()))
    os.execl(os.path.abspath(__file__), "")

# BOT
bot = commands.Bot(command_prefix = '!')
bot.remove_command("help")

# load files
loadfiles()

# COMMANDS
# restart command
@commands.has_permissions(administrator=True)
@bot.command(aliases = ['reload'], pass_context = True)
async def restart(ctx):
    global current_path
    global batch_data

    # log the use of restart command
    print("\n{}: Rebooting due to restart command.\n".format(getLogFormattedTime()))

    # signal that bot is rebooting
    await bot.add_reaction(ctx.message, '♻')

    # save the message
    file = open(current_path + "/restart_msg.pkl", "wb")
    pickle.dump(ctx.message, file, 4)
    file.close()

    # save batch mode data
    file = open(current_path + "/batch_data.pkl", "wb")
    pickle.dump(batch_data, file, 4)
    file.close()

    # properly shut down
    await bot.logout()

    # restart
    os.execl(os.path.abspath(__file__), "")

# bot status
@bot.command(pass_context = True)
async def status(ctx):
    pver = sys.version_info
    
    status_embed = discord.Embed(title = "Ready.")
    status_embed.set_thumbnail(url = bot.user.avatar_url)
    status_embed.add_field(name = "discord.py version", value = "%s, running under Python %d.%d.%d" % (discord.__version__, pver[0], pver[1], pver[2]))
    status_embed.set_footer(text = "To read about how to use the SauceBot, use `!sauce` or `!sauce help`")

    await bot.send_message(ctx.message.channel, embed = status_embed)

# reload files
@commands.has_permissions(administrator=True)
@bot.command(aliases = ["loadfiles"], pass_context = True)
async def reloadfiles(ctx):
    loadfiles()
    await bot.add_reaction(ctx.message, '✅')

# main sauce command
@bot.command(pass_context = True, aliases = ["s"])
async def sauce(ctx, *, text: str = None):
    # analyze the message to decide what's the user's intent
    result = analyzeCommand(ctx.message, text)

    if result == None or result == "help":
        await bot.send_message(ctx.message.channel, sauce_help)

    elif result == "file":
        # get urls of attached file(s)
        urls = getAttachmentURLs(ctx.message)
        # iterate over urls and create percent encoded links with them
        for u in urls:
            await bot.send_message(ctx.message.channel, allSources(u))

    elif result == "link":
        await bot.send_message(ctx.message.channel, allSources(text))

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
                await bot.send_message(ctx.message.channel, allSources(u))
        else:
            await bot.send_message(ctx.message.channel, "Linked message does not have attached pictures.")

    return

# batch mode
@bot.command(pass_context = True, aliases = ["b"])
async def batch(ctx, *, text: str = None):
    global batch_data

    temp_embed = discord.Embed(description = "Preparing batch mode for you...")
    msg_sent = await bot.send_message(ctx.message.channel, embed = temp_embed)
    await bot.add_reaction(msg_sent, '🇸')
    await bot.add_reaction(msg_sent, '🇬')
    await bot.add_reaction(msg_sent, '🇹')
    await bot.add_reaction(msg_sent, 'ℹ')
    await bot.add_reaction(msg_sent, '🇾')
    await bot.add_reaction(msg_sent, '✅')
    await bot.add_reaction(msg_sent, '🛑')

    if batch_data.get((ctx.message.author.id, ctx.message.channel.id), None) == None:
        batch_data[(ctx.message.author.id, ctx.message.channel.id)] = set()

    services = batch_data.get((ctx.message.author.id, ctx.message.channel.id))

    loop = True
    while(loop):
        # embed with current state of batch mode for user using the command
        batch_embed = discord.Embed(title = "Batch mode", colour = 0xb29a80)

        batch_embed.add_field(name = "What is batch mode", value = "Batch mode allows you to find sources for large quantities of pictures. When enabled for at least one service, every time you send a message with attached picture(s), in response you will reveive link(s) that allow you to check with just one click if the source is known. Remember, in batch mode only *pictures attached* will be checked, not any links in messages.")

        batch_embed.add_field(name = "How to control batch mode", value = "Toggle single services with appropriate reactions. To confirm what you set, use :white_check_mark:. To disable them all and stop batch mode, use :stop_sign:")

        embed_content = ""
        if "s" in services:
            embed_content += ":white_check_mark: SauceNAO\n"
        else:
            embed_content += ":x: SauceNAO\n"

        if "g" in services:
            embed_content += ":white_check_mark: Google\n"
        else:
            embed_content += ":x: Google\n"

        if "t" in services:
            embed_content += ":white_check_mark: TinEye\n"
        else:
            embed_content += ":x: TinEye\n"

        if "i" in services:
            embed_content += ":white_check_mark: IQDB\n"
        else:
            embed_content += ":x: IQDB\n"

        if "y" in services:
            embed_content += ":white_check_mark: Yandex"
        else:
            embed_content += ":x: Yandex"

        batch_embed.add_field(name = "Enabled reverse search engines for {}:".format(ctx.message.author.name), value = embed_content)
        msg_sent = await bot.edit_message(msg_sent, embed = batch_embed)

        def check(reaction: discord.Reaction, user: discord.Member):
            return user == ctx.message.author
        res = await bot.wait_for_reaction(message=msg_sent, check = check)
        await bot.remove_reaction(msg_sent, res.reaction.emoji, ctx.message.author)

        if(res.reaction.emoji == '🇸'):     # toggle saucenao
            if "s" in services:
                services.discard("s")
            else:
                services.add("s")

        if(res.reaction.emoji == '🇬'):     # toggle google
            if "g" in services:
                services.discard("g")
            else:
                services.add("g")

        if(res.reaction.emoji == '🇹'):     # toggle tineye
            if "t" in services:
                services.discard("t")
            else:
                services.add("t")

        if(res.reaction.emoji == 'ℹ'):      # toggle iqdb
            if "i" in services:
                services.discard("i")
            else:
                services.add("i")

        if(res.reaction.emoji == '🇾'):      # toggle yandex
            if "y" in services:
                services.discard("y")
            else:
                services.add("y")

        if(res.reaction.emoji == '✅'):
            await bot.delete_message(msg_sent)
            await bot.send_message(ctx.message.channel, ":white_check_mark: Your settings have been saved.")
            loop = False

        if(res.reaction.emoji == '🛑'):
            # disable all services
            services.clear()

            await bot.delete_message(msg_sent)
            await bot.send_message(ctx.message.channel, ":stop_sign: You have stopped batch mode. All services have been disabled.")
            loop = False

# universal on_message function
@bot.event
async def on_message(message: discord.Message):
    global batch_data

    if message.author == bot.user:
        return      # don't reply to yourself

    # don't do anything if user wants to control batch mode
    if message.content.startswith("!b") or message.content.startswith("!batch"):
        await bot.process_commands(message)
        return

    # if given user has batch mode enabled for given channel
    services = batch_data.get((message.author.id, message.channel.id), None)
    if services != None:
        if len(services) > 0:
            urls = getAttachmentURLs(message)
            if len(urls) > 0:
                for u in urls:
                    response = ""
                    if "s" in services:
                        response += sauceLink(u) + '\n'
                    if "g" in services:
                        response += googleLink(u) + '\n'
                    if "t" in services:
                        response += tineyeLink(u) + '\n'
                    if "i" in services:
                        response += iqdbLink(u) + '\n'
                    if "y" in services:
                        response += yandexLink(u)
                    await bot.send_message(message.channel, response)
            else:
                await bot.send_message(message.channel, "{}, you're in batch mode in this channel. If you want to disable it, use `!batch`!".format(message.author.mention))

    await bot.process_commands(message)

# command exception handler
@bot.event
async def on_command_error(exception, ctx: discord.ext.commands.Context):
    # if user tried using an unknown command
    if type(exception) == discord.ext.commands.errors.CommandNotFound:
        # do nothing
        pass

# what to do on successful boot
@bot.event
async def on_ready():
    global current_path
    global batch_data

    print("###\n[{}]: k. running as {}, discord.py version {}\n###".format(getLogFormattedTime(), bot.user.name, discord.__version__))

    await bot.change_presence(game=discord.Game(name="!sauce", url=None, type=0), status=None, afk=False)

    # if the bot bot was restarted with a restart message, tick it after the restart
    if os.path.exists(current_path + "/restart_msg.pkl"):
        file = open(current_path + "/restart_msg.pkl", "rb")
        r_msg = pickle.load(file)
        file.close()
        await bot.remove_reaction(r_msg, '♻', bot.user)
        await bot.add_reaction(r_msg, '✅')
        os.remove(current_path + "/restart_msg.pkl")

    if os.path.exists(current_path + "/batch_data.pkl"):
        file = open(current_path + "/batch_data.pkl", "rb")
        batch_data = pickle.load(file)
        file.close()
        os.remove(current_path + "/batch_data.pkl")

try:
    bot.run(token_str)
except:
    # in case of any error, restart the bot
    file = open(current_path + "/batch_data.pkl", "wb")
    pickle.dump(batch_data, file, 4)
    file.close()

    restartHandler()