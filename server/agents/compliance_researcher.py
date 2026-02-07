"""
Agent 1: Compliance Researcher (Dedalus)

Looks up live 2026 SEC/FINRA regulations relevant to the document type using
Dedalus SDK with Brave Search MCP, then returns structured compliance rules
for Agent 2 (PDF Analyzer) to compare against.

Falls back to hardcoded rules when Dedalus is unavailable.

Owner: Person 1
"""

import json
import logging
import os
from datetime import date
from typing import Optional, List

from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic models for Dedalus structured output
# ---------------------------------------------------------------------------
class ComplianceRule(BaseModel):
    """A single compliance rule returned by the research agent."""
    rule_id: str
    description: str
    severity: str  # "critical", "high", "medium", "low"
    regulation: str
    source_url: Optional[str] = None


class ResearchResult(BaseModel):
    """Structured output from the Dedalus compliance researcher."""
    rules_text: str
    rules: List[ComplianceRule]
    required_sections: List[str]
    materiality_threshold: str
    sources: List[str]


# ---------------------------------------------------------------------------
# Dedalus-powered research
# ---------------------------------------------------------------------------
_SEARCH_QUERIES = {
    "SOX 404": "SOX 404 Section compliance requirements PCAOB COSO 2025 2026",
    "10-K": "SEC Regulation S-K 10-K annual report filing requirements 2025 2026",
    "8-K": "SEC Form 8-K current report disclosure requirements 2025 2026",
    "Invoice": "GAAP invoice compliance internal controls standards 2025 2026",
}

_PROMPT_TEMPLATE = """You are a financial compliance researcher. Your task is to research and compile the current compliance requirements for {doc_type} documents.

Use web search to find the most up-to-date {year} SEC, FINRA, PCAOB, and GAAP regulations that apply to {doc_type} filings/documents.

For each requirement you find, provide:
1. A unique rule_id (e.g., "SOX-ITGC-1", "SEC-1A", etc.)
2. A clear description of what is required
3. Severity: "critical" (mandatory, failure = enforcement action), "high" (strongly required), or "medium" (best practice)
4. The specific regulation reference (e.g., "SOX Section 404(a) — COSO Framework CC5.1")
5. The source URL where you found this information (if available)

Also identify:
- The mandatory sections that must be present in a compliant {doc_type} document
- The materiality threshold that applies

Format your response as structured data with:
- rules_text: A comprehensive plain-text summary of all rules (this will be fed to the PDF analyzer)
- rules: Array of individual rules with rule_id, description, severity, regulation, source_url
- required_sections: List of section names that must be present
- materiality_threshold: The applicable materiality threshold as a string
- sources: List of URLs consulted

Focus on actionable, specific requirements — not general guidance. Include 5-8 rules covering the most critical compliance areas."""


async def _research_with_dedalus(document_type: str) -> dict:
    """
    Use Dedalus SDK + Brave Search MCP to fetch live regulations.

    Returns a dict matching the pipeline's expected interface:
        {"rules": str, "sources": list[str], "last_updated": str}
    """
    from dedalus_labs import AsyncDedalus, DedalusRunner

    client = AsyncDedalus()
    runner = DedalusRunner(client)

    prompt = _PROMPT_TEMPLATE.format(
        doc_type=document_type,
        year=date.today().year,
    )

    result = await runner.run(
        input=prompt,
        model="openai/gpt-4o",
        mcp_servers=["tsion/brave-search-mcp"],
        response_format=ResearchResult,
        max_steps=5,
    )

    # Parse the Dedalus response
    if hasattr(result, "final_output") and result.final_output:
        output = result.final_output

        if isinstance(output, ResearchResult):
            return _research_result_to_dict(output)

        # Try JSON parsing if it came back as a string
        try:
            data = json.loads(output) if isinstance(output, str) else output
            parsed = ResearchResult(**data)
            return _research_result_to_dict(parsed)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            logger.warning("Could not parse Dedalus output: %s", exc)
            # If we got a raw text response, use it directly as rules text
            if isinstance(output, str) and len(output) > 100:
                return {
                    "rules": output,
                    "sources": [],
                    "last_updated": date.today().isoformat(),
                }

    raise RuntimeError("Dedalus returned no usable output")


def _research_result_to_dict(result: ResearchResult) -> dict:
    """Convert a ResearchResult Pydantic model to the dict the pipeline expects."""
    # Build a rich rules_text if the model didn't provide one
    rules_text = result.rules_text
    if not rules_text or len(rules_text) < 50:
        lines = []
        for r in result.rules:
            lines.append(
                f"- [{r.severity.upper()}] {r.rule_id}: {r.description} "
                f"(Reference: {r.regulation})"
            )
        if result.required_sections:
            lines.append(
                f"\nRequired sections: {', '.join(result.required_sections)}"
            )
        if result.materiality_threshold:
            lines.append(
                f"Materiality threshold: {result.materiality_threshold}"
            )
        rules_text = "\n".join(lines)

    sources = result.sources or []
    # Also gather source_urls from individual rules
    for r in result.rules:
        if r.source_url and r.source_url not in sources:
            sources.append(r.source_url)

    return {
        "rules": rules_text,
        "sources": sources,
        "last_updated": date.today().isoformat(),
    }


# ---------------------------------------------------------------------------
# Hardcoded fallback rules
# ---------------------------------------------------------------------------
_FALLBACK_RULES = {
    "SOX 404": {
        "rules": (
            "SOX Section 404 — Internal Control over Financial Reporting\n\n"
            "1. ITGC Documentation (CRITICAL)\n"
            "   IT General Controls must be fully documented for all financial "
            "reporting systems, including change management, logical access, "
            "and computer operations. Reference: COSO Framework CC5.1\n\n"
            "2. Segregation of Duties (CRITICAL)\n"
            "   Transaction initiation, authorization, recording, and custody "
            "must be performed by separate individuals. No single person should "
            "control multiple stages. Reference: PCAOB AS 2201.22\n\n"
            "3. Quarterly Access Reviews (HIGH)\n"
            "   Access logs for financial systems must be reviewed at least "
            "quarterly with formal sign-off from compliance officers. Annual "
            "reviews are insufficient. Reference: COSO CC6.1\n\n"
            "4. Risk Assessment Process (HIGH)\n"
            "   Management must document a formal risk assessment identifying "
            "risks to reliable financial reporting and the controls that "
            "mitigate them. Reference: SOX 404 Risk Assessment\n\n"
            "5. Monitoring and Deficiency Tracking (MEDIUM)\n"
            "   Ongoing monitoring activities must be in place with a formal "
            "process for tracking, escalating, and remediating control "
            "deficiencies. Reference: SOX 404 Monitoring\n\n"
            "6. Management Assessment and Testing (CRITICAL)\n"
            "   Management must perform its own assessment of internal controls "
            "and document the basis for its conclusions. Reference: SEC Rule "
            "33-8238\n"
        ),
        "sources": [
            "https://www.sec.gov/rules/final/33-8238.htm",
            "https://pcaobus.org/oversight/standards/auditing-standards/details/AS2201",
            "https://www.coso.org/guidance-on-ic",
        ],
        "last_updated": "2026-01-15",
    },
    "10-K": {
        "rules": (
            "SEC Regulation S-K — 10-K Annual Report Requirements\n\n"
            "1. Risk Factors — Item 105 (CRITICAL)\n"
            "   Registrants must disclose the most significant factors that "
            "make an investment speculative or risky, organized by relevance. "
            "Generic risk factors are insufficient. Reference: Reg S-K Item 105\n\n"
            "2. MD&A — Item 303 (CRITICAL)\n"
            "   Management's Discussion and Analysis must include known trends, "
            "demands, commitments, events, or uncertainties that are reasonably "
            "likely to have a material effect. Forward-looking statements "
            "required. Reference: Reg S-K Item 303\n\n"
            "3. Financial Statements — Item 8 (CRITICAL)\n"
            "   Audited financial statements and supplementary data must be "
            "included with an independent auditor's report. Reference: Reg S-K "
            "Item 8\n\n"
            "4. Controls & Procedures — Item 9A (HIGH)\n"
            "   Disclosure of management's conclusions about the effectiveness "
            "of disclosure controls and procedures. Must include any changes "
            "in internal controls. Reference: Reg S-K Item 9A\n\n"
            "5. XBRL/iXBRL Tagging (MEDIUM)\n"
            "   Financial statements must be tagged in iXBRL format. All line "
            "items require appropriate tagging. Reference: SEC Rule 405 Reg S-T\n\n"
            "6. Executive Compensation — Item 402 (HIGH)\n"
            "   Full disclosure of compensation for named executive officers "
            "including summary compensation table. Reference: Reg S-K Item 402\n"
        ),
        "sources": [
            "https://www.sec.gov/divisions/corpfin/guidance/regs-kinterp.htm",
            "https://www.sec.gov/rules/final/2020/33-10825.htm",
        ],
        "last_updated": "2026-01-15",
    },
    "8-K": {
        "rules": (
            "SEC Form 8-K — Current Report Requirements\n\n"
            "1. Timeliness (CRITICAL)\n"
            "   Material events must be disclosed within 4 business days of "
            "occurrence. Late filings may trigger enforcement action. "
            "Reference: SEC Rule 13a-11\n\n"
            "2. Material Definitive Agreements — Item 1.01 (CRITICAL)\n"
            "   Entry into or termination of material contracts must be "
            "disclosed with key terms and conditions. Reference: Form 8-K "
            "Item 1.01\n\n"
            "3. Acquisition or Disposition — Item 2.01 (CRITICAL)\n"
            "   Completion of material acquisitions or dispositions must be "
            "reported including purchase price, assets acquired, and funding "
            "sources. Reference: Form 8-K Item 2.01\n\n"
            "4. Officer Changes — Item 5.02 (HIGH)\n"
            "   Departure or appointment of principal officers and directors "
            "must be disclosed. Reference: Form 8-K Item 5.02\n\n"
            "5. Financial Statements — Item 9.01 (HIGH)\n"
            "   Financial statements and exhibits as required by the triggering "
            "event must be filed or incorporated by reference. Reference: "
            "Form 8-K Item 9.01\n\n"
            "6. Material Impairments — Item 2.06 (MEDIUM)\n"
            "   Material charges for impairment must be disclosed with the "
            "facts and circumstances leading to the conclusion. Reference: "
            "Form 8-K Item 2.06\n"
        ),
        "sources": [
            "https://www.sec.gov/about/forms/form8-k.pdf",
            "https://www.sec.gov/rules/final/2004/33-8400.htm",
        ],
        "last_updated": "2026-01-15",
    },
    "Invoice": {
        "rules": (
            "Invoice Compliance — GAAP & Internal Control Standards\n\n"
            "1. Mathematical Accuracy (HIGH)\n"
            "   Line item totals must sum to the invoice total. Tax "
            "calculations must be verifiable and match applicable jurisdiction "
            "rates. Reference: GAAP Invoice Standards\n\n"
            "2. Authorization Signatures (CRITICAL)\n"
            "   Invoices exceeding $10,000 require an authorized signature. "
            "Approval authority matrix must be documented and followed. "
            "Reference: Internal Controls — Invoice Approval\n\n"
            "3. Three-Way Match (HIGH)\n"
            "   Invoice must match the purchase order and goods receipt. "
            "Discrepancies above $1,000 require investigation and sign-off. "
            "Reference: Internal Controls — Procurement\n\n"
            "4. Duplicate Detection (HIGH)\n"
            "   Invoice numbers must be unique. Systems must flag potential "
            "duplicates by number, amount, and vendor within a rolling "
            "12-month window. Reference: Internal Controls — Duplicate "
            "Detection\n\n"
            "5. Tax Compliance (MEDIUM)\n"
            "   Tax calculations must comply with the applicable jurisdiction "
            "rates. Tax-exempt transactions require valid exemption "
            "certificates on file. Reference: State Tax Compliance\n\n"
            "6. Purchase Order Reference (MEDIUM)\n"
            "   Invoices exceeding $5,000 must reference a valid purchase "
            "order. Exceptions require documented approval. Reference: "
            "Procurement Controls\n"
        ),
        "sources": [
            "https://www.irs.gov/businesses/small-businesses-self-employed/keeping-records",
            "https://www.fasb.org/standards",
        ],
        "last_updated": "2026-01-15",
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
async def research_compliance_rules(
    document_type: str,
    specific_topics: Optional[List[str]] = None,
) -> dict:
    """
    Research current compliance rules for the given document type.

    Attempts live research via Dedalus SDK + Brave Search MCP.
    Falls back to hardcoded rules if Dedalus is unavailable or errors out.

    Called by the pipeline orchestrator (Person 2). Returns a dict consumed
    as ``compliance_research.get("rules", "")``.

    Args:
        document_type: 'SOX 404' | '10-K' | '8-K' | 'Invoice'
        specific_topics: Optional list of specific areas to research.

    Returns:
        dict with:
        - rules: str — full text of applicable rules
        - sources: list[str] — URLs of sources consulted
        - last_updated: str — when rules were last updated
    """
    # Try Dedalus-powered live research first
    if os.getenv("DEDALUS_API_KEY"):
        try:
            print(f"[Agent 1] Attempting Dedalus research for {document_type}...")
            result = await _research_with_dedalus(document_type)
            rules_text = result.get("rules", "")
            if rules_text and len(rules_text) > 50:
                print(f"[Agent 1] >>> SUCCESS: Live research completed ({len(rules_text)} chars generated)")
                return result
            print(f"[Agent 1] Dedalus returned insufficient rules for {document_type}, using fallback")
        except ImportError as exc:
            print(f"[Agent 1] dedalus_labs not installed: {exc} — using fallback rules")
        except Exception as exc:
            print(f"[Agent 1] Dedalus research FAILED for {document_type}: {type(exc).__name__}: {exc} — using fallback")
    else:
        print("[Agent 1] DEDALUS_API_KEY not set, using fallback rules")

    # Fallback to hardcoded rules
    result = _FALLBACK_RULES.get(document_type)
    if result is not None:
        print(f"[Agent 1] >>> NOTICE: Using hardcoded FALLBACK rules for {document_type}")
        return result

    return {
        "rules": "Standard financial compliance requirements apply.",
        "sources": [],
        "last_updated": "2026-01-01",
    }
