"""
Northstar Discord Bot — Financial Compliance Auditor

Entry point for the Discord bot. Loads slash commands and connects to Discord.
"""

import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("northstar-bot")

# ---------------------------------------------------------------------------
# Bot setup
# ---------------------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
@bot.event
async def on_ready():
    logger.info("Bot logged in as %s", bot.user)
    logger.info("Connected to %d guild(s)", len(bot.guilds))

    # Sync slash commands with Discord
    try:
        synced = await bot.tree.sync()
        logger.info("Synced %d command(s)", len(synced))
    except Exception as exc:
        logger.error("Failed to sync commands: %s", exc)


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
):
    """Global error handler for application (slash) commands."""
    logger.error("Command error in /%s: %s", interaction.command.name if interaction.command else "unknown", error)

    # If we haven't responded yet, send an ephemeral error
    if not interaction.response.is_done():
        await interaction.response.send_message(
            "An unexpected error occurred. Please try again later.",
            ephemeral=True,
        )
    else:
        await interaction.followup.send(
            "An unexpected error occurred. Please try again later.",
            ephemeral=True,
        )


# ---------------------------------------------------------------------------
# Command loading
# ---------------------------------------------------------------------------
async def load_commands():
    from commands import audit, history, audit_detail

    await audit.setup(bot)
    await history.setup(bot)
    await audit_detail.setup(bot)
    logger.info("All commands loaded")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token or token == "your_token_here":
        logger.error(
            "DISCORD_BOT_TOKEN is not set. "
            "Copy .env.example to .env and add your token."
        )
        sys.exit(1)

    asyncio.run(load_commands())
    bot.run(token)


if __name__ == "__main__":
    main()
