import logging

import discord
from discord import app_commands

from services.api_client import FastAPIClient, APIError
from services.embed_builder import (
    build_audit_result_embed,
    build_processing_embed,
    build_error_embed,
)

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


async def setup(bot: discord.ext.commands.Bot):
    """Register the /audit slash command."""
    client = FastAPIClient()

    @bot.tree.command(
        name="audit",
        description="Run compliance audit on a financial document",
    )
    @app_commands.describe(
        document_type="Type of financial document",
        file="PDF file to audit (max 50 MB)",
    )
    @app_commands.choices(
        document_type=[
            app_commands.Choice(name="SOX 404", value="SOX 404"),
            app_commands.Choice(name="10-K", value="10-K"),
            app_commands.Choice(name="Invoice", value="Invoice"),
        ]
    )
    async def audit(
        interaction: discord.Interaction,
        document_type: str,
        file: discord.Attachment,
    ):
        # Defer immediately — audit can take a while
        await interaction.response.defer()

        # --- Validation ---
        if not file.filename.lower().endswith(".pdf"):
            await interaction.followup.send(
                embed=build_error_embed("Please upload a PDF file."),
                ephemeral=True,
            )
            return

        if file.size > MAX_FILE_SIZE:
            await interaction.followup.send(
                embed=build_error_embed("File must be under 50 MB."),
                ephemeral=True,
            )
            return

        # --- Send processing indicator ---
        await interaction.followup.send(embed=build_processing_embed())

        # --- Download attachment ---
        try:
            pdf_bytes = await file.read()
        except discord.HTTPException:
            await interaction.edit_original_response(
                embed=build_error_embed(
                    "Failed to download the attachment. Please try again."
                )
            )
            return

        # --- Call backend ---
        try:
            result = await client.run_audit(
                user_id=str(interaction.user.id),
                pdf_bytes=pdf_bytes,
                filename=file.filename,
                document_type=document_type,
            )
        except TimeoutError:
            await interaction.edit_original_response(
                embed=build_error_embed(
                    "Audit is taking longer than expected. "
                    "Please check `/history` later for your results."
                )
            )
            return
        except APIError as exc:
            logger.error("Audit API error: %s", exc)
            await interaction.edit_original_response(
                embed=build_error_embed(
                    "The audit service returned an error. Please try again."
                )
            )
            return
        except Exception as exc:
            logger.exception("Unexpected error during audit: %s", exc)
            await interaction.edit_original_response(
                embed=build_error_embed(
                    "An unexpected error occurred. Please try again later."
                )
            )
            return

        # --- Display results ---
        result_embed = build_audit_result_embed(result)
        await interaction.edit_original_response(embed=result_embed)

        # --- Attach PDF report ---
        report_url = result.get("report_pdf_url")
        if report_url:
            try:
                pdf_data = await client.download_pdf(report_url)
                if pdf_data:
                    filename = f"report_{result['audit_id']}.pdf"
                    await interaction.followup.send(
                        content="Here is your full audit report:",
                        file=discord.File(
                            fp=__import__("io").BytesIO(pdf_data),
                            filename=filename,
                        ),
                    )
            except Exception as exc:
                logger.warning("Failed to attach PDF report: %s", exc)
