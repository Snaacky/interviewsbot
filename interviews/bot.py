import glob
import logging
import os

import discord
from discord.ext import commands

import __init__  # noqa
import database
from config import config


bot = commands.Bot(
    command_prefix=config["bot"]["prefix"],
    intents=discord.Intents(
        messages=config["bot"]["intents"]["messages"],
        message_content=config["bot"]["intents"]["message_content"],
        guilds=config["bot"]["intents"]["guilds"],
        members=config["bot"]["intents"]["members"],
        bans=config["bot"]["intents"]["bans"],
        reactions=config["bot"]["intents"]["reactions"],
    ),
    case_insensitive=config["bot"]["case_insensitive"],
    help_command=None,
)
log = logging.getLogger(__name__)


@bot.event
async def on_ready() -> None:
    log.info(f"Logged in as: {str(bot.user)}")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name=config["bot"]["status"])
    )


def clean_cog_name(cog: str):
    return cog.replace("/", ".").replace("\\", ".").replace(".py", "")


if __name__ == "__main__":
    for cog in glob.iglob(os.path.join("cogs", "**", "[!^_]*.py"), root_dir=os.path.dirname(__file__), recursive=True):
        bot.load_extension(clean_cog_name(cog))
    database.Database().setup()
    bot.run(config["bot"]["token"])
