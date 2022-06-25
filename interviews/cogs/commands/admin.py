import io
import logging
import textwrap
import traceback
from contextlib import redirect_stdout

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog

from interviews.utils import embeds


log = logging.getLogger(__name__)


class AdministrationCommands(Cog):
    """
    This class is legacy code that needs to eventually be
    split into separate files and removed from the codebase.

    The eval command cannot be ported to slash commands until Discord
    supports slash command parameters with multiple lines of input.

    We will eventually migrate the embed generators into a slash
    command based embed generator system where the embed generators
    below will be stored as presets that can be spawned via slash
    commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._last_result = None

    def _cleanup_code(self, content) -> str:
        """
        Automatically removes code blocks from the code.
        """
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

    @commands.is_owner()
    @commands.command(name="eval")
    async def eval(self, ctx, *, body: str):
        """
        Evaluates input as Python code.
        """
        # Required environment variables.
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "embeds": embeds,
            "_": self._last_result,
        }
        # Creating embed.
        embed = discord.Embed(title="Evaluating.", color=0xB134EB)
        env.update(globals())

        # Calling cleanup command to remove the markdown traces.
        body = self._cleanup_code(body)
        embed.add_field(name="Input:", value=f"```py\n{body}\n```", inline=False)
        # Output stream.
        stdout = io.StringIO()

        # Exact code to be compiled.
        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            # Attempting execution
            exec(to_compile, env)
        except Exception as e:
            # In case there's an error, add it to the embed, send and stop.
            errors = f"```py\n{e.__class__.__name__}: {e}\n```"
            embed.add_field(name="Errors:", value=errors, inline=False)
            await ctx.send(embed=embed)
            return errors

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            # In case there's an error, add it to the embed, send and stop.
            value = stdout.getvalue()
            errors = f"```py\n{value}{traceback.format_exc()}\n```"
            embed.add_field(name="Errors:", value=errors, inline=False)
            await ctx.send(embed=embed)

        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except Exception:
                pass

            if ret is None:
                if value:
                    # Output.
                    output = f"```py\n{value}\n```"
                    embed.add_field(name="Output:", value=output, inline=False)
                    await ctx.send(embed=embed)
            else:
                # Maybe the case where there's no output?
                self._last_result = ret
                output = f"```py\n{value}{ret}\n```"
                embed.add_field(name="Output:", value=output, inline=False)
                await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(AdministrationCommands(bot))
    log.info("Commands loaded: administration")
