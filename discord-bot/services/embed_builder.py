import discord
from datetime import datetime
from typing import List

EMBED_FIELD_LIMIT = 1024  # Discord's max for embed field values


def _truncate(text: str, limit: int = EMBED_FIELD_LIMIT) -> str:
    """Truncate text to fit within Discord's embed field limit."""
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


# Grade → embed colour mapping
GRADE_COLORS = {
    "A": 0x00FF00,  # Green
    "B": 0x0099FF,  # Blue
    "C": 0xFFCC00,  # Yellow
    "D": 0xFF9900,  # Orange
    "F": 0xFF0000,  # Red
}

# Severity → emoji mapping
SEVERITY_EMOJI = {
    "critical": "\U0001f534",  # Red circle
    "high": "\U0001f7e0",      # Orange circle
    "medium": "\U0001f7e1",    # Yellow circle
    "low": "\U0001f7e2",       # Green circle
}


def build_audit_result_embed(audit_data: dict) -> discord.Embed:
    """
    Builds a rich embed for audit completion results.

    Colour is determined by the letter grade (A-F).
    Shows score, document type, top 3 gaps, and timestamp.
    """
    grade = audit_data.get("grade", "F")
    color = GRADE_COLORS.get(grade, 0xFF0000)

    embed = discord.Embed(
        title=f"\U0001f4ca Audit Complete: {audit_data['document_name']}",
        description=audit_data.get("executive_summary", ""),
        color=color,
    )

    # Score & grade
    embed.add_field(
        name="Compliance Score",
        value=f"**{audit_data['score']}/100** (Grade **{grade}**)",
        inline=True,
    )

    # Document type
    embed.add_field(
        name="Document Type",
        value=audit_data["document_type"],
        inline=True,
    )

    # Top 3 gaps — each as its own field to avoid the 1024 char limit
    gaps = audit_data.get("gaps", [])[:3]
    for gap in gaps:
        emoji = SEVERITY_EMOJI.get(gap["severity"], "\u26aa")
        field_value = f"{gap['description']}\n*{gap['regulation']}*"
        embed.add_field(
            name=f"{emoji} {gap['title']}",
            value=_truncate(field_value),
            inline=False,
        )

    # Timestamp
    ts = audit_data.get("timestamp", "")
    if ts:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            embed.add_field(
                name="Timestamp",
                value=dt.strftime("%b %d, %Y %I:%M %p UTC"),
                inline=True,
            )
        except ValueError:
            embed.add_field(name="Timestamp", value=ts, inline=True)

    embed.set_footer(text=f"Audit ID: {audit_data['audit_id']}")
    return embed


def build_detail_embed(audit_data: dict) -> discord.Embed:
    """
    Builds a detailed embed showing ALL gaps and remediation steps.
    Used by the /audit-detail command.
    """
    grade = audit_data.get("grade", "F")
    color = GRADE_COLORS.get(grade, 0xFF0000)

    embed = discord.Embed(
        title=f"\U0001f4ca Audit Detail: {audit_data['document_name']}",
        description=audit_data.get("executive_summary", ""),
        color=color,
    )

    embed.add_field(
        name="Compliance Score",
        value=f"**{audit_data['score']}/100** (Grade **{grade}**)",
        inline=True,
    )
    embed.add_field(
        name="Document Type",
        value=audit_data["document_type"],
        inline=True,
    )

    # All gaps — each as its own field
    gaps = audit_data.get("gaps", [])
    for gap in gaps:
        emoji = SEVERITY_EMOJI.get(gap["severity"], "\u26aa")
        field_value = f"{gap['description']}\n*{gap['regulation']}*"
        embed.add_field(
            name=f"{emoji} {gap['title']}",
            value=_truncate(field_value),
            inline=False,
        )

    # Remediation steps
    remediation = audit_data.get("remediation", [])
    if remediation:
        steps = "\n".join(f"**{i+1}.** {step}" for i, step in enumerate(remediation))
        embed.add_field(
            name="Remediation Steps",
            value=_truncate(steps),
            inline=False,
        )

    # Timestamp
    ts = audit_data.get("timestamp", "")
    if ts:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            embed.add_field(
                name="Timestamp",
                value=dt.strftime("%b %d, %Y %I:%M %p UTC"),
                inline=True,
            )
        except ValueError:
            embed.add_field(name="Timestamp", value=ts, inline=True)

    embed.set_footer(text=f"Audit ID: {audit_data['audit_id']}")
    return embed


def build_history_embed(audits: List[dict]) -> discord.Embed:
    """
    Builds an embed showing the user's audit history.
    Shows the 10 most recent audits with scores and dates.
    """
    embed = discord.Embed(
        title="\U0001f4dc Audit History",
        color=0x5865F2,  # Discord blurple
    )

    display = audits[:10]
    lines = []
    for a in display:
        grade = a.get("grade", "?")
        emoji = SEVERITY_EMOJI.get(
            "critical" if grade in ("D", "F") else "medium" if grade == "C" else "low",
            "\u26aa",
        )
        ts = a.get("timestamp", "")
        date_str = ""
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                date_str = dt.strftime("%m/%d/%Y")
            except ValueError:
                date_str = ts[:10]
        lines.append(
            f"{emoji} **{a['document_name']}** — "
            f"{a['score']}/100 ({grade}) — {date_str}\n"
            f"`{a['audit_id']}`"
        )

    embed.description = "\n\n".join(lines)

    if len(audits) > 10:
        embed.set_footer(text=f"Showing 10 most recent of {len(audits)} audits")
    else:
        embed.set_footer(text=f"{len(audits)} audit(s) total")

    return embed


def build_processing_embed() -> discord.Embed:
    """Simple 'Processing your audit...' embed with loading indicator."""
    return discord.Embed(
        title="\u23f3 Processing Your Audit...",
        description=(
            "Your document is being analyzed by our compliance pipeline.\n"
            "This may take up to 2 minutes."
        ),
        color=0x5865F2,
    )


def build_error_embed(error_message: str) -> discord.Embed:
    """Error embed in red with error details."""
    return discord.Embed(
        title="\u274c Error",
        description=error_message,
        color=0xFF0000,
    )
