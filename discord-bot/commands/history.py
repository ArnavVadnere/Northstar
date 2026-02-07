import logging

import discord

from services.api_client import FastAPIClient, APIError
from services.embed_builder import build_history_embed, build_error_embed

logger = logging.getLogger(__name__)


async def setup(bot: discord.ext.commands.Bot):
    """Register the /history slash command."""
    client = FastAPIClient()

    @bot.tree.command(
        name="history",
        description="View your past audit history",
    )
    async def history(interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            data = await client.get_history(str(interaction.user.id))
        except APIError as exc:
            logger.error("History API error: %s", exc)
            await interaction.followup.send(
                embed=build_error_embed(
                    "Failed to fetch audit history. Please try again."
                )
            )
            return
        except Exception as exc:
            logger.exception("Unexpected error fetching history: %s", exc)
            await interaction.followup.send(
                embed=build_error_embed(
                    "An unexpected error occurred. Please try again later."
                )
            )
            return

        audits = data.get("audits", [])
        if not audits:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="\U0001f4dc Audit History",
                    description=(
                        "You haven't run any audits yet.\n"
                        "Use `/audit` to get started!"
                    ),
                    color=0x5865F2,
                )
            )
            return

        embed = build_history_embed(audits)
        await interaction.followup.send(embed=embed)
