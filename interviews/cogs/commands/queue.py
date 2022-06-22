import logging

import discord
from interviews.utils import embeds
from discord.commands import context, slash_command
from discord.ext import commands

from interviews import config


log = logging.getLogger(__name__)


class QueueCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.queue = []

    @slash_command(
        guild_ids=config["guild_ids"],
        description="Join the interview queue.",
    )
    async def queue(self, ctx: context.ApplicationContext) -> None:
        await ctx.defer(ephemeral=True)
        await embeds.success_message(ctx=ctx, description="Added")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(QueueCommands(bot))
    log.info("Commands loaded: queue")
