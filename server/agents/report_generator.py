"""
Agent 3: Report Generator (Dedalus)

Synthesizes analysis results into a compliance report with score,
executive summary, remediation steps, and PDF report.

Uses Dedalus SDK with structured outputs for reliable JSON responses.

Owner: Person 3
"""
import os
import json
from typing import Optional, List
from pathlib import Path
from pydantic import BaseModel
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()


# --- Pydantic models for structured output ---

class ReportOutput(BaseModel):
    """Structured output from the report generator agent."""
    remediation: List[str]
    executive_summary: str


# --- Score and grade calculation ---

def _calculate_score(gaps: List[dict]) -> int:
    """Calculate compliance score based on gap severity.

    Weights are calibrated so that real SEC-accepted filings with minor
    gaps still score in the B/C range, while documents with genuine
    material deficiencies score D/F.
    """
    severity_weights = {"critical": 15, "high": 8, "medium": 3}
    total_penalty = sum(
        severity_weights.get(g.get("severity", "medium"), 3) for g in gaps
    )
    return max(0, 100 - total_penalty)


def _calculate_grade(score: int) -> str:
    """Map score to letter grade per CONTRACT.md."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


# --- Main agent function ---

async def generate_report(
    audit_id: str,
    document_name: str,
    document_type: str,
    gaps: List[dict],
    output_dir: Optional[Path] = None
) -> dict:
    """
    Generate a compliance report from analysis results.

    Args:
        audit_id: Unique audit identifier
        document_name: Original document filename
        document_type: Type of document
        gaps: List of compliance gaps from Agent 2
        output_dir: Directory to save generated PDF

    Returns:
        dict with: score, grade, remediation, executive_summary, report_pdf_url
    """
    score = _calculate_score(gaps)
    grade = _calculate_grade(score)

    # Build the report PDF path
    report_filename = f"report_{audit_id}.pdf"
    if output_dir:
        report_path = output_dir / report_filename
    else:
        report_path = Path("generated_reports") / report_filename

    # Ensure parent directory exists
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Relative URL for the frontend
    report_pdf_url = f"/api/files/{report_filename}"

    # If Dedalus is not configured, use fallback
    if not os.getenv("DEDALUS_API_KEY"):
        result = _fallback_report(score, grade, gaps, document_type)
        result["report_pdf_url"] = report_pdf_url
        _generate_pdf(result, gaps, document_name, document_type, report_path)
        return result

    # Format gaps for the prompt
    gaps_summary = json.dumps(gaps, indent=2)

    prompt = f"""You are a senior compliance officer writing an audit report.

DOCUMENT AUDITED:
- Filename: {document_name}
- Type: {document_type}
- Compliance Score: {score}/100 (Grade: {grade})

COMPLIANCE GAPS IDENTIFIED:
{gaps_summary}

TASK:
Generate two things:

1. EXECUTIVE SUMMARY (3-5 sentences):
   - Written for C-suite executives
   - State the number and severity of gaps found
   - Mention the compliance score and grade
   - Highlight the most critical finding
   - Recommend whether immediate action is needed

2. REMEDIATION STEPS (exactly 5 steps):
   - Specific, actionable steps to address the identified gaps
   - Ordered by priority (most urgent first)
   - Each step should reference which gap it addresses
   - Include timeframes (e.g., "within 30 days")
   - Be concrete, not generic
   - If fewer than 5 gaps, add general best-practice remediation steps to reach exactly 5.

Return JSON with:
{{
  "executive_summary": "Your executive summary here",
  "remediation": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]
}}"""

    try:
        client = AsyncDedalus()
        runner = DedalusRunner(client)

        result = await runner.run(
            input=prompt,
            model="openai/gpt-4o",
            response_format=ReportOutput,
            max_steps=3
        )

        # Parse the response
        report_data = {
            "score": score,
            "grade": grade,
            "remediation": [],
            "executive_summary": "",
            "report_pdf_url": report_pdf_url,
        }

        if hasattr(result, "final_output") and result.final_output:
            if isinstance(result.final_output, ReportOutput):
                report_data["remediation"] = result.final_output.remediation
                report_data["executive_summary"] = result.final_output.executive_summary
            else:
                # Try parsing as JSON string
                try:
                    data = json.loads(str(result.final_output))
                    report_data["remediation"] = data.get("remediation", [])
                    report_data["executive_summary"] = data.get("executive_summary", "")
                except (json.JSONDecodeError, TypeError):
                    pass

        # Ensure we have data, otherwise fallback
        if not report_data["executive_summary"] or not report_data["remediation"]:
             raise ValueError("Empty or invalid response from Dedalus")

        # Force exactly 5 remediation items
        report_data["remediation"] = _ensure_five_items(report_data["remediation"])

        _generate_pdf(report_data, gaps, document_name, document_type, report_path)
        return report_data

    except Exception as e:
        print(f"Dedalus report generation failed: {e}")
        fallback = _fallback_report(score, grade, gaps, document_type)
        fallback["report_pdf_url"] = report_pdf_url
        _generate_pdf(fallback, gaps, document_name, document_type, report_path)
        return fallback


def _ensure_five_items(items: List[str]) -> List[str]:
    """Ensure list has exactly 5 items."""
    if len(items) >= 5:
        return items[:5]

    defaults = [
        "Document all remediation actions taken with supporting evidence for audit trail.",
        "Conduct training for relevant personnel on updated compliance requirements.",
        "Schedule a follow-up compliance review within 60 days to verify remediation effectiveness.",
        "Update internal control documentation to reflect current processes.",
        "Establish a continuous monitoring program for high-risk areas."
    ]

    needed = 5 - len(items)
    return items + defaults[:needed]


def _fallback_report(score: int, grade: str, gaps: List[dict], document_type: str) -> dict:
    """Generate a report without Dedalus when API key is not available."""
    critical_count = sum(1 for g in gaps if g.get("severity") == "critical")
    high_count = sum(1 for g in gaps if g.get("severity") == "high")
    medium_count = sum(1 for g in gaps if g.get("severity") == "medium")

    # Build severity breakdown string
    parts = []
    if critical_count:
        parts.append(f"{critical_count} critical")
    if high_count:
        parts.append(f"{high_count} high")
    if medium_count:
        parts.append(f"{medium_count} medium")
    severity_text = ", ".join(parts) if parts else "various"

    executive_summary = (
        f"The audit of the {document_type} document identified {len(gaps)} compliance gaps "
        f"({severity_text} severity). "
        f"The overall compliance score is {score}/100 (Grade: {grade}). "
    )
    if critical_count:
        first_critical = next(g for g in gaps if g.get("severity") == "critical")
        executive_summary += (
            f"The most critical finding involves {first_critical.get('title', 'a critical deficiency').lower()}. "
            f"Immediate remediation is required for critical findings before the next reporting cycle."
        )
    elif high_count:
        executive_summary += (
            "High-priority gaps should be addressed within 30 days. "
            "A follow-up review should be scheduled after remediation actions are completed."
        )
    else:
        executive_summary += (
            "The compliance posture is satisfactory with minor improvements recommended. "
            "A follow-up review should be scheduled within the next quarter."
        )

    # Build remediation steps from actual gaps
    remediation = []
    for gap in gaps[:5]:
        severity = gap.get("severity", "medium")
        title = gap.get("title", "identified gap")
        timeframe = {"critical": "within 14 days", "high": "within 30 days", "medium": "within 60 days"}
        remediation.append(
            f"Address \"{title}\" {timeframe.get(severity, 'within 60 days')} "
            f"by reviewing compliance with {gap.get('regulation', 'applicable regulations')}."
        )

    return {
        "score": score,
        "grade": grade,
        "remediation": _ensure_five_items(remediation),
        "executive_summary": executive_summary,
    }


def _generate_pdf(
    report: dict,
    gaps: List[dict],
    document_name: str,
    document_type: str,
    output_path: Path,
) -> None:
    """Generate a PDF compliance report using reportlab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        print("reportlab not installed, skipping PDF generation")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=20, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], fontSize=11,
        textColor=HexColor("#666666"), spaceAfter=20
    )
    heading_style = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"], fontSize=14,
        spaceBefore=16, spaceAfter=8
    )
    body_style = ParagraphStyle(
        "ReportBody", parent=styles["Normal"], fontSize=10,
        leading=14, spaceAfter=8
    )

    severity_colors = {
        "critical": HexColor("#DC2626"),
        "high": HexColor("#F97316"),
        "medium": HexColor("#EAB308"),
    }

    elements: list = []

    # Cover
    elements.append(Paragraph("Compliance Audit Report", title_style))
    elements.append(Paragraph(
        f"{document_name} &bull; {document_type}", subtitle_style
    ))

    # Score card
    score = report["score"]
    grade = report["grade"]
    score_color = "#16A34A" if score >= 80 else "#EAB308" if score >= 60 else "#DC2626"
    score_data = [
        ["Compliance Score", "Grade"],
        [
            Paragraph(f'<font color="{score_color}" size="24"><b>{score}</b></font>/100', body_style),
            Paragraph(f'<font color="{score_color}" size="24"><b>{grade}</b></font>', body_style),
        ],
    ]
    score_table = Table(score_data, colWidths=[3 * inch, 3 * inch])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F3F4F6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#374151")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#E5E7EB")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 12))

    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    elements.append(Paragraph(report["executive_summary"], body_style))

    # Findings
    elements.append(Paragraph("Findings", heading_style))
    for gap in gaps:
        severity = gap.get("severity", "medium")
        color = severity_colors.get(severity, HexColor("#6B7280"))
        elements.append(Paragraph(
            f'<font color="{color}"><b>[{severity.upper()}]</b></font> '
            f'<b>{gap.get("title", "Finding")}</b>',
            body_style,
        ))
        elements.append(Paragraph(gap.get("description", ""), body_style))
        elements.append(Paragraph(
            f'<i>Regulation: {gap.get("regulation", "N/A")}</i>', body_style
        ))
        elements.append(Spacer(1, 8))

    # Remediation Steps
    elements.append(Paragraph("Remediation Steps", heading_style))
    for i, step in enumerate(report.get("remediation", []), 1):
        elements.append(Paragraph(f"<b>{i}.</b> {step}", body_style))

    try:
        doc.build(elements)
        print(f"[Agent 3] PDF report generated: {output_path}")
    except Exception as e:
        print(f"[Agent 3] PDF generation failed: {e}")
