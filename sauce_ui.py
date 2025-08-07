"""Functions and classes for building nice looking bot UI."""

import discord

# embed builders
def warning_embed(message: str) -> discord.Embed:
    """Return a warning-style embed with provided message."""
    embed = discord.Embed(description=f":warning: {message}", color=0xffcc4d)
    return embed

def info_embed(message: str) -> discord.Embed:
    """Return a information-style embed with provided message."""
    embed = discord.Embed(description=f":information_source: {message}", color=0x3b88c3)
    return embed

def ok_embed(message: str) -> discord.Embed:
    """Return a confirmation-style embed with provided message."""
    embed = discord.Embed(description=f":white_check_mark: {message}", color=0x77b255)
    return embed

def gear_embed(message: str) -> discord.Embed:
    """Return a processing-style embed with provided message."""
    embed = discord.Embed(description=f":gear: {message}", color=0x66757f)
    return embed

def question_embed(message: str) -> discord.Embed:
    """Return a question-style embed with provided message."""
    embed = discord.Embed(description=f":grey_question: {message}", color=0xccd6dd)
    return embed

def bot_info_embed(embed_color: int, avatar_url: str) -> discord.Embed:
    """Return a ready-made embed with general information about the bot."""
    embed = discord.Embed(title="SauceBot", description="Serving the sauce since 2018.", url="https://github.com/PoldekPL/SauceBot", color=embed_color)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="\u200b", value="SauceBot has one purpose, to make finding ~~sauce~~ source for pictures easier. Provide a picture or a link and you'll be one click away from finding the original.", inline=False)
    embed.add_field(name="Usage", value="To learn about how to use the SauceBot, send a message with `sauce.help`.", inline=False)
    embed.set_footer(text="-- SauceBot written by PoldekPL. --")

    return embed