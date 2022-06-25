import logging
import time

import discord
from discord.commands import context
from discord.ext import commands
from discord.ui import InputText, Modal

from interviews import config, database
from interviews.utils import embeds, strings


log = logging.getLogger(__name__)


class QueueInteractions(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.bot.add_view(JoinQueueButton())

    @commands.is_owner()
    @commands.command(name="createqueueembed")
    async def create_queue_embed(self, ctx: context.ApplicationContext) -> None:
        embed = embeds.make_embed(
            title="Interview Queue",
            description=strings.INTERVIEW_QUEUE_EMBED,
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed, view=JoinQueueButton())


class JoinQueueButton(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.primary, custom_id="join_queue", emoji="🗳️")
    async def join_queue(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        category = discord.utils.get(interaction.guild.categories, id=config["categories"]["tickets"])
        ticket = discord.utils.get(category.text_channels, name=f"ticket-{interaction.user.id}")

        if ticket:
            embed = embeds.make_embed(
                color=discord.Color.red(),
                title="Error:",
                description=f"{interaction.user.mention}, you already have a ticket open at: {ticket.mention}",
            )
            return await interaction.response.send_message(embed=embed, view=None, ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(QueueInteractions(bot))
    log.info("Interactions loaded: queue")
