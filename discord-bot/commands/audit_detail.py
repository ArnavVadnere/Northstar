import io
import logging

import discord
from discord import app_commands

from services.api_client import FastAPIClient, APIError, AuditNotFoundError
from services.embed_builder import build_detail_embed, build_error_embed

logger = logging.getLogger(__name__)


async def setup(bot: discord.ext.commands.Bot):
    """Register the /audit-detail slash command."""
    client = FastAPIClient()

    @bot.tree.command(
        name="audit-detail",
        description="View detailed results for a specific audit",
    )
    @app_commands.describe(audit_id="Audit ID (e.g., aud_abc123)")
    async def audit_detail(interaction: discord.Interaction, audit_id: str):
        await interaction.response.defer()

        try:
            result = await client.get_audit_detail(audit_id)
        except AuditNotFoundError:
            await interaction.followup.send(
                embed=build_error_embed(
                    f"No audit found with ID `{audit_id}`.\n"
                    "Use `/history` to see your past audits."
                )
            )
            return
        except APIError as exc:
            logger.error("Audit detail API error: %s", exc)
            await interaction.followup.send(
                embed=build_error_embed(
                    "Failed to fetch audit details. Please try again."
                )
            )
            return
        except Exception as exc:
            logger.exception("Unexpected error fetching audit detail: %s", exc)
            await interaction.followup.send(
                embed=build_error_embed(
                    "An unexpected error occurred. Please try again later."
                )
            )
            return

        embed = build_detail_embed(result)
        await interaction.followup.send(embed=embed)

        # Attach PDF report if available
        report_url = result.get("report_pdf_url")
        if report_url:
            try:
                pdf_data = await client.download_pdf(report_url)
                if pdf_data:
                    await interaction.followup.send(
                        content="Full audit report:",
                        file=discord.File(
                            fp=io.BytesIO(pdf_data),
                            filename=f"report_{audit_id}.pdf",
                        ),
                    )
            except Exception as exc:
                logger.warning("Failed to attach PDF report: %s", exc)
