import logging

import discord
from discord.ext import commands
from discord.commands import context, slash_command, Option

from interviews import config
from interviews.utils import embeds

log = logging.getLogger(__name__)


class StaffCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @slash_command(guild_ids=config["guild_ids"], description="Grab users from queue and create interview rooms")
    @commands.has_role(config["roles"]["staff"])
    async def interview(
        self,
        ctx: context.ApplicationContext,
        count: Option(
            str, description="Number of members to add to rooms", choices=["1", "2", "3", "4", "5"], required=True
        ),
    ) -> None:
        await ctx.defer(ephemeral=True)

        channel = discord.utils.get(ctx.guild.text_channels, id=config["channels"]["staff"]["interviewers"])
        if channel is not ctx.channel:
            return await embeds.error_message(ctx=ctx, description=f"This command can only be ran in {channel.mention}")

        queue = self.bot.get_cog("QueueCommands")
        if not queue.queue:
            return await embeds.error_message(ctx=ctx, description="There are no users currently in queue.")

        if len(queue.queue) < int(count):
            count = queue.queue
            await embeds.success_message(ctx=ctx, description=(f"Added {len(count)} user(s) into interview rooms."))

    def create_interview_room(ctx, user_id: int):
        staff = discord.utils.get(ctx.guild.roles, id=config["roles"]["staff"])
        user = discord.utils.get(ctx.guild.members, id=user_id)
        permission = {
            staff: discord.PermissionOverwrite(read_messages=True),
            ctx.guild.default_role: discord.PermissionOverwrite(
                read_messages=False,
                manage_channels=False,
                manage_permissions=False,
                manage_messages=False,
            ),
            user: discord.PermissionOverwrite(read_messages=True),
        }


def setup(bot: commands.Bot) -> None:
    bot.add_cog(StaffCommands(bot))
    log.info("Commands loaded: staff")
