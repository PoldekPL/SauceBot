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

# helper function for getting formatted time for log
def getLogFormattedTime():
    timestamp_now = time.gmtime()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", timestamp_now)

    return formatted_time

# # function to ensure proper restart of the bot in case of irrecoverable error
# def restartHandler():
#     # test for internet connection before restarting the bot
#     # for good measure, test two different IP addresses
#     while subprocess.run(args = ['ping', '-c', '1', '8.8.8.8'], stdout = subprocess.DEVNULL).returncode != 0 and subprocess.run(args = ['ping', '-c', '1', '1.1.1.1'], stdout = subprocess.DEVNULL).returncode != 0:
#         time.sleep(3)

#     print("[{}]: Had to restart with restartHandler".format(getLogFormattedTime()))
#     os.execl(os.path.abspath(__file__), "")


class SauceBot(commands.Bot):

    # CONSTANTS
    current_path = sys.path[0]

    # VARIABLES
    token_str = ""              # bot login token
    sauce_help = []             # help message
    # batch_data = {}             # batch mode data about who, where and what services
    embed_colors = {}           # colors to use for embeds for each server the bot is in

    def __init__(self):
        intents = discord.Intents(guilds = True,
                                  members = True,
                                  messages = True,
                                  reactions = True)

        super().__init__(command_prefix=["sauce.", "s."], intents=intents)
        
        self.loadfiles()

        self.remove_command("help")

        self.add_cog(SauceCommands(self))

    async def on_ready(self):
        # global batch_data

        print("[{}]: #BOOT# k. running as {}, discord.py version {}".format(getLogFormattedTime(), self.user.name, discord.__version__))

        # populate the dict of embed colors for each server
        for g in self.guilds:
            self.embed_colors[g.id] = g.me.color.value

        # if the bot was restarted with a restart message, tick it after the restart
        if os.path.exists(self.current_path + "/restart_msg_id"):
            file = open(self.current_path + "/restart_msg_id", "r")
            r_msg = file.read()
            file.close()
            msg_ids = r_msg.split()

            # get the server
            msg_guild = self.get_guild(int(msg_ids[0]))
            # get the channel in the server
            msg_channel = msg_guild.get_channel(int(msg_ids[1]))
            # get the message in the channel... in the server
            msg = await msg_channel.fetch_message(int(msg_ids[2]))

            await msg.remove_reaction('♻', self.user)
            await msg.add_reaction('✅')
            os.remove(self.current_path + "/restart_msg_id")

        # if os.path.exists(current_path + "/batch_data.pkl"):
        #     file = open(current_path + "/batch_data.pkl", "rb")
        #     batch_data = pickle.load(file)
        #     file.close()
        #     os.remove(current_path + "/batch_data.pkl")

    async def on_message(self, message: discord.Message):
        # global batch_data

        if message.author == self.user:
            return      # don't reply to yourself

        #     # don't do anything if user wants to control batch mode
        #     if message.content.startswith("!b") or message.content.startswith("!batch"):
        #         await bot.process_commands(message)
        #         return

        #     # if given user has batch mode enabled for given channel
        #     services = batch_data.get((message.author.id, message.channel.id), None)
        #     if services != None:
        #         if len(services) > 0:
        #             urls = getAttachmentURLs(message)
        #             if len(urls) > 0:
        #                 for u in urls:
        #                     response = ""
        #                     if "s" in services:
        #                         response += sauceLink(u) + '\n'
        #                     if "g" in services:
        #                         response += googleLink(u) + '\n'
        #                     if "t" in services:
        #                         response += tineyeLink(u) + '\n'
        #                     if "i" in services:
        #                         response += iqdbLink(u) + '\n'
        #                     if "y" in services:
        #                         response += yandexLink(u)
        #                     await bot.send_message(message.channel, response)
        #             else:
        #                 await bot.send_message(message.channel, "{}, you're in batch mode in this channel. If you want to disable it, use `!batch`!".format(message.author.mention))

        await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        # if user tried using an unknown command
        if type(exception) == discord.ext.commands.errors.CommandNotFound:
            # do nothing
            pass
        else:
            print("[{}]: Encountered CommandError:".format(getLogFormattedTime()))
            await super().on_command_error(ctx, exception)

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if after.id == self.user.id:
            self.embed_colors[after.guild.id] = after.color.value

    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        if after in after.guild.me.roles:
            self.embed_colors[after.guild.id] = after.guild.me.color.value

    async def on_guild_join(self, guild):
        self.embed_colors[guild.id] = guild.me.color.value

    async def on_guild_remove(self, guild):
        del self.embed_colors[guild.id]

    def loadfiles(self):
        file = open(self.current_path + "/token", "r")
        self.token_str = file.read()
        file.close()

        file2 = open(self.current_path + "/sauce_help", "r")
        help_str = file2.read()
        self.sauce_help = help_str.split('$')
        file2.close()

        return

    def run(self):
        # I am not sure if reconnect=True does anything but I saw it in a different bot, so why not. I always had problems with bot stability using old discord.py library
        super().run(self.token_str, reconnect=True)

# COMMANDS
class SauceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="all", aliases=["a"])
    async def sauceAll(self, ctx):
        await self.replyLinks(ctx, saucenao=True, google=True, tineye=True, iqdb=True, yandex=True)

    # a majestic function name, I know
    @commands.command(name="saucenao", aliases=["sauce", "s", "e621", "e"])
    async def sauceSauce(self, ctx):
        await self.replyLinks(ctx, saucenao=True)

    @commands.command(name="google", aliases=["g"])
    async def sauceGoogle(self, ctx):
        await self.replyLinks(ctx, google=True)

    @commands.command(name="tineye", aliases=["t"])
    async def sauceTineye(self, ctx):
        await self.replyLinks(ctx, tineye=True)

    @commands.command(name="iqdb", aliases=["i"])
    async def sauceIQDB(self, ctx):
        await self.replyLinks(ctx, iqdb=True)

    @commands.command(name="yandex", aliases=["y"])
    async def sauceYandex(self, ctx):
        await self.replyLinks(ctx, yandex=True)

    async def replyLinks(self, ctx, saucenao=False, google=False, tineye=False, iqdb=False, yandex=False):
        # analyze the message to decide what's the user's intent
        result = self.analyzeCommand(ctx)

        # let's build a list of urls to generate links with
        urls = []
        if result == "file":
            # user attached file(s), get url(s)
            urls = self.getMessageAttachmentURLs(ctx.message)

        elif result == "link":
            # user has sent a string, assume it's a valin picture url
            link = ctx.message.content.replace(ctx.prefix + ctx.invoked_with, "").strip()
            urls = [link]

        elif result == "discord link":
            # user linked a discord message, extract server, channel and message ids
            ids = re.findall(r"\d+", ctx.message.content, re.I)

            # get the server
            linked_guild = self.bot.get_guild(int(ids[0]))
            # get the channel in the server
            linked_channel = linked_guild.get_channel(int(ids[1]))
            # get the message in the channel... in the server
            linked_message = await linked_channel.fetch_message(int(ids[2]))

            # get the possible urls
            urls = self.getMessageAttachmentURLs(linked_message)

            if len(urls) == 0:
                await ctx.send(":warning: Linked message does not have attached pictures.")
                return

        else: # result == None
            await ctx.send(":grey_question: You have not provided anything to perform reverse search on. If you want to learn how to use SauceBot, send `sauce.help`.")
            return

        index = 1
        # iterate over attachments and provide search links for them
        for u in urls:
            embed = discord.Embed(color=self.bot.embed_colors[ctx.guild.id])
            embed.set_thumbnail(url=self.bot.user.avatar_url)

            if result == "file":
                embed.title = ":mag_right: Reverse searching attached files"
                embed.add_field(name="Attachment {} of {}:".format(index, len(urls)), value=u, inline=False)

            elif result == "link":
                embed.title = ":mag_right: Reverse searching provided link"
                embed.add_field(name="Provided link:", value=u, inline=False)

            if result == "discord link":
                embed.title = ":mag_right: Reverse searching images attached to linked message"
                link = ctx.message.content.replace(ctx.prefix + ctx.invoked_with, "").strip()
                embed.add_field(name="Linked message:", value=link, inline=False)
                embed.add_field(name="Found attachment {} of {}:".format(index, len(urls)), value=u, inline=False)

            if saucenao == True:
                embed.add_field(name="\u200b", value="**[SauceNAO]({})\n**".format(self.sauceLink(u)), inline=False)
            if google == True:
                embed.add_field(name="\u200b", value="**[Google]({})\n**".format(self.googleLink(u)), inline=False)
            if tineye == True:
                embed.add_field(name="\u200b", value="**[TinEye]({})\n**".format(self.tineyeLink(u)), inline=False)
            if iqdb == True:
                embed.add_field(name="\u200b", value="**[IQDB]({})\n**".format(self.iqdbLink(u)), inline=False)
            if yandex == True:
                embed.add_field(name="\u200b", value="**[Yandex]({})**".format(self.yandexLink(u)), inline=False)

            await ctx.send(embed=embed)
            del embed
            index += 1
        return

    def sauceLink(self, url: str):
        return "https://saucenao.com/search.php?url={}".format(parse.quote_plus(url))

    def googleLink(self, url: str):
        return "https://www.google.com/searchbyimage?&image_url={}".format(parse.quote_plus(url))

    def tineyeLink(self, url: str):
        return "https://www.tineye.com/search?url={}".format(parse.quote_plus(url))

    def iqdbLink(self, url: str):
        return "https://iqdb.org/?url={}".format(parse.quote_plus(url))

    def yandexLink(self, url: str):
        return "https://yandex.com/images/search?url={}&rpt=imageview".format(parse.quote_plus(url))

    # ananlyze the command called by the user
    def analyzeCommand(self, ctx: commands.Context):
        # NOTE: I know that using strings as return values is rather lazy, but it's not meant to be a *high performance* bot

        # if message body is empty (there is no text after the command)
        if (ctx.prefix + ctx.invoked_with) == ctx.message.content:
            # if there is a file (or files) attached
            if len(ctx.message.attachments) > 0:
                return "file"
            else:
                # no message, no attachments.
                return None
        else:
            # the command is followed by some text, detect if that's a valid discord message permalink
            if re.search(r"(ptb\.|canary\.){0,1}https://discordapp\.com/channels/\d+/\d+/\d+", ctx.message.content, re.I) != None:
                return "discord link"
            # if not, assume that's just a link to a picture. it's user's responsibility to make sure it's valid
            else:
                return "link"

    def getMessageAttachmentURLs(self, message: discord.Message):
        urls = []

        # iterate over attached files and get their urls
        for a in message.attachments:
            urls.append(a.url)

        return urls

    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(title="SauceBot", description="Serving the sauce since 2018.", url="https://github.com/PoldekPL/SauceBot", color=self.bot.embed_colors[ctx.guild.id])
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="\u200b", value="SauceBot has one purpose, to make finding ~~sauce~~ source for pictures easier. Provide a picture, select one (or all) search engines and you'll be one click away from finding the original.", inline=False)
        embed.add_field(name="Usage", value="To learn about how to use the SauceBot, send a message with `sauce.help`.", inline=False)
        embed.set_footer(text="-- SauceBot written by PoldekPL#0105. --")
        await ctx.send(embed=embed)

    @commands.command()
    async def status(self, ctx):
        pver = sys.version_info
        
        status_embed = discord.Embed(title="Ready.", color=self.bot.embed_colors[ctx.guild.id])
        status_embed.set_thumbnail(url=self.bot.user.avatar_url)
        status_embed.add_field(name="discord.py version:", value="%s, running under Python %d.%d.%d" % (discord.__version__, pver[0], pver[1], pver[2]))
        status_embed.set_footer(text="To read about how to use the SauceBot, use sauce.help")

        await ctx.send(embed=status_embed)

    @commands.command(name="help", aliases=["h"])
    async def helpCommand(self, ctx):
        for part in self.bot.sauce_help:
            await ctx.send(part)

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['reload'])
    async def restart(self, ctx):
        # log the use of restart command
        print("[{}]: Received restart command.".format(getLogFormattedTime()))

        # signal that bot is rebooting
        await ctx.message.add_reaction('♻')

        # save the message ids
        file = open(self.bot.current_path + "/restart_msg_id", "w")
        file.write(str(ctx.guild.id) + ' ' + str(ctx.channel.id) + ' ' + str(ctx.message.id))
        file.close()

        # # save batch mode data
        # file = open(current_path + "/batch_data.pkl", "wb")
        # pickle.dump(batch_data, file, 4)
        # file.close()

        # properly shut down
        await self.bot.logout()

        # restart
        print("[{}]: Rebooting...".format(getLogFormattedTime()))
        os.execl(os.path.abspath(__file__), " ")

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=["loadfiles"])
    async def reloadfiles(self, ctx):
        print("[{}]: Reloading input files.".format(getLogFormattedTime()))
        self.bot.loadfiles()
        await ctx.message.add_reaction('✅')

# # batch mode
# @bot.command(pass_context = True, aliases = ["b"])
# async def batch(ctx, *, text: str = None):
#     global batch_data

#     temp_embed = discord.Embed(description = "Preparing batch mode for you...")
#     msg_sent = await bot.send_message(ctx.message.channel, embed = temp_embed)
#     await bot.add_reaction(msg_sent, '🇸')
#     await bot.add_reaction(msg_sent, '🇬')
#     await bot.add_reaction(msg_sent, '🇹')
#     await bot.add_reaction(msg_sent, 'ℹ')
#     await bot.add_reaction(msg_sent, '🇾')
#     await bot.add_reaction(msg_sent, '✅')
#     await bot.add_reaction(msg_sent, '🛑')

#     if batch_data.get((ctx.message.author.id, ctx.message.channel.id), None) == None:
#         batch_data[(ctx.message.author.id, ctx.message.channel.id)] = set()

#     services = batch_data.get((ctx.message.author.id, ctx.message.channel.id))

#     loop = True
#     while(loop):
#         # embed with current state of batch mode for user using the command
#         batch_embed = discord.Embed(title = "Batch mode", colour = 0xb29a80)

#         batch_embed.add_field(name = "What is batch mode", value = "Batch mode allows you to find sources for large quantities of pictures. When enabled for at least one service, every time you send a message with attached picture(s), in response you will reveive link(s) that allow you to check with just one click if the source is known. Remember, in batch mode only *pictures attached* will be checked, not any links in messages.")

#         batch_embed.add_field(name = "How to control batch mode", value = "Toggle single services with appropriate reactions. To confirm what you set, use :white_check_mark:. To disable them all and stop batch mode, use :stop_sign:")

#         embed_content = ""
#         if "s" in services:
#             embed_content += ":white_check_mark: SauceNAO\n"
#         else:
#             embed_content += ":x: SauceNAO\n"

#         if "g" in services:
#             embed_content += ":white_check_mark: Google\n"
#         else:
#             embed_content += ":x: Google\n"

#         if "t" in services:
#             embed_content += ":white_check_mark: TinEye\n"
#         else:
#             embed_content += ":x: TinEye\n"

#         if "i" in services:
#             embed_content += ":white_check_mark: IQDB\n"
#         else:
#             embed_content += ":x: IQDB\n"

#         if "y" in services:
#             embed_content += ":white_check_mark: Yandex"
#         else:
#             embed_content += ":x: Yandex"

#         batch_embed.add_field(name = "Enabled reverse search engines for {}:".format(ctx.message.author.name), value = embed_content)
#         msg_sent = await bot.edit_message(msg_sent, embed = batch_embed)

#         def check(reaction: discord.Reaction, user: discord.Member):
#             return user == ctx.message.author
#         res = await bot.wait_for_reaction(message=msg_sent, check = check)
#         await bot.remove_reaction(msg_sent, res.reaction.emoji, ctx.message.author)

#         if(res.reaction.emoji == '🇸'):     # toggle saucenao
#             if "s" in services:
#                 services.discard("s")
#             else:
#                 services.add("s")

#         if(res.reaction.emoji == '🇬'):     # toggle google
#             if "g" in services:
#                 services.discard("g")
#             else:
#                 services.add("g")

#         if(res.reaction.emoji == '🇹'):     # toggle tineye
#             if "t" in services:
#                 services.discard("t")
#             else:
#                 services.add("t")

#         if(res.reaction.emoji == 'ℹ'):      # toggle iqdb
#             if "i" in services:
#                 services.discard("i")
#             else:
#                 services.add("i")

#         if(res.reaction.emoji == '🇾'):      # toggle yandex
#             if "y" in services:
#                 services.discard("y")
#             else:
#                 services.add("y")

#         if(res.reaction.emoji == '✅'):
#             await bot.delete_message(msg_sent)
#             await bot.send_message(ctx.message.channel, ":white_check_mark: Your settings have been saved.")
#             loop = False

#         if(res.reaction.emoji == '🛑'):
#             # disable all services
#             services.clear()

#             await bot.delete_message(msg_sent)
#             await bot.send_message(ctx.message.channel, ":stop_sign: You have stopped batch mode. All services have been disabled.")
#             loop = False

if __name__ == "__main__":
    # for now, the restartHandler() will be left out. we'll see how stable bot is using new version of discord.py

    # try:
    bot = SauceBot()
    bot.run()
    # except:
    #     # in case of any error, restart the bot
    #     file = open(current_path + "/batch_data.pkl", "wb")
    #     pickle.dump(batch_data, file, 4)
    #     file.close()

    #     restartHandler()