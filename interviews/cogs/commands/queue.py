import logging

import discord
from discord.commands import context, slash_command
from discord.ext import commands

from interviews import config
from interviews.utils import embeds

log = logging.getLogger(__name__)


class QueueCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.rooms = {}
        self.queue = []

    @slash_command(guild_ids=config["guild_ids"], description="Get your current position in queue")
    @commands.has_role(config["roles"]["queueable"])
    async def position(self, ctx: context.ApplicationContext) -> None:
        await ctx.defer(ephemeral=True)

        channel = discord.utils.get(ctx.guild.text_channels, id=config["channels"]["queue"]["queue"])
        if channel is not ctx.channel:
            return await embeds.error_message(ctx=ctx, description=f"This command can only be ran in {channel.mention}")

        if ctx.author.id not in self.queue:
            return await embeds.error_message(ctx=ctx, description="You are not in queue.")

        await embeds.success_message(
            ctx=ctx,
            description=f"You are in position {self.queue.index(ctx.author.id) + 1} out of {len(self.queue)}.",
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(QueueCommands(bot))
    log.info("Commands loaded: queue")
