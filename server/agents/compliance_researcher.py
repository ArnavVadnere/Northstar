"""
Agent 1 — Compliance Researcher

Accepts a document type and returns structured compliance rules relevant to
that document type. Called by Person 2's pipeline orchestrator.

TODO: Replace hardcoded rules with Dedalus SDK + web search MCP to fetch
      live 2026 SEC/FINRA regulations.
"""

from typing import List

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
class ComplianceRule(BaseModel):
    rule_id: str
    description: str
    severity: str  # "critical", "high", "medium", "low"
    regulation: str


class ComplianceRulesSchema(BaseModel):
    rules: List[ComplianceRule]
    required_sections: List[str]
    materiality_threshold: str


# ---------------------------------------------------------------------------
# Rule definitions (MVP hardcoded — replace with Dedalus agent)
# ---------------------------------------------------------------------------
_SOX_404_RULES = ComplianceRulesSchema(
    rules=[
        ComplianceRule(
            rule_id="SOX-ITGC-1",
            description="IT General Controls testing must be documented",
            severity="critical",
            regulation="SOX 404 Section A",
        ),
        ComplianceRule(
            rule_id="SOX-ACCESS-1",
            description="Access controls and segregation of duties required",
            severity="critical",
            regulation="SOX 404 Section B",
        ),
        ComplianceRule(
            rule_id="SOX-MGMT-1",
            description="Management letter findings must be addressed",
            severity="high",
            regulation="SOX 404 Management Requirements",
        ),
        ComplianceRule(
            rule_id="SOX-RISK-1",
            description="Risk assessment process must be documented with identified risks",
            severity="high",
            regulation="SOX 404 Risk Assessment",
        ),
        ComplianceRule(
            rule_id="SOX-MONITOR-1",
            description="Ongoing monitoring activities and deficiency tracking required",
            severity="medium",
            regulation="SOX 404 Monitoring",
        ),
    ],
    required_sections=[
        "IT Controls",
        "Access Management",
        "Change Management",
        "Risk Assessment",
        "Monitoring Activities",
    ],
    materiality_threshold="$5M for financial statement impact",
)

_10K_RULES = ComplianceRulesSchema(
    rules=[
        ComplianceRule(
            rule_id="SEC-1A",
            description="Risk factors section (Item 1A) is mandatory",
            severity="critical",
            regulation="SEC Regulation S-K Item 1A",
        ),
        ComplianceRule(
            rule_id="SEC-7",
            description="Management's Discussion and Analysis (MD&A) required",
            severity="critical",
            regulation="SEC Regulation S-K Item 7",
        ),
        ComplianceRule(
            rule_id="SEC-9A",
            description="Controls and Procedures disclosure required",
            severity="high",
            regulation="SEC Regulation S-K Item 9A",
        ),
        ComplianceRule(
            rule_id="SEC-8",
            description="Financial statements and supplementary data must be audited",
            severity="critical",
            regulation="SEC Regulation S-K Item 8",
        ),
        ComplianceRule(
            rule_id="SEC-XBRL",
            description="XBRL/iXBRL tagging required for financial statements",
            severity="medium",
            regulation="SEC Rule 405 of Regulation S-T",
        ),
    ],
    required_sections=[
        "Risk Factors",
        "MD&A",
        "Financial Statements",
        "Controls & Procedures",
        "Auditor's Report",
    ],
    materiality_threshold="5% of net income or $100K, whichever is lower",
)

_INVOICE_RULES = ComplianceRulesSchema(
    rules=[
        ComplianceRule(
            rule_id="INV-MATH-1",
            description="Line item totals must equal invoice total",
            severity="high",
            regulation="GAAP Invoice Standards",
        ),
        ComplianceRule(
            rule_id="INV-SIG-1",
            description="Authorized signature required for invoices >$10K",
            severity="critical",
            regulation="Internal Controls - Invoice Approval",
        ),
        ComplianceRule(
            rule_id="INV-TAX-1",
            description="Tax calculations must comply with jurisdiction rates",
            severity="medium",
            regulation="State Tax Compliance",
        ),
        ComplianceRule(
            rule_id="INV-DUP-1",
            description="Duplicate invoice numbers must be flagged",
            severity="high",
            regulation="Internal Controls - Duplicate Detection",
        ),
        ComplianceRule(
            rule_id="INV-PO-1",
            description="Purchase order reference required for invoices >$5K",
            severity="medium",
            regulation="Procurement Controls",
        ),
    ],
    required_sections=["Line Items", "Totals", "Tax", "Payment Terms", "Vendor Info"],
    materiality_threshold="$1,000 for math discrepancies",
)

_RULES_BY_TYPE = {
    "SOX 404": _SOX_404_RULES,
    "10-K": _10K_RULES,
    "Invoice": _INVOICE_RULES,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
async def research_compliance_rules(document_type: str) -> ComplianceRulesSchema:
    """
    Agent 1: Research current compliance regulations for the given document type.

    This agent is called by Person 2's pipeline orchestrator.

    Args:
        document_type: "SOX 404" | "10-K" | "Invoice"

    Returns:
        ComplianceRulesSchema with current 2026 regulations.
    """
    # TODO: Implement Dedalus agent with web search MCP for live regulation lookup.
    # For MVP, return hardcoded realistic rules.
    result = _RULES_BY_TYPE.get(document_type)
    if result is not None:
        return result

    # Fallback for unknown document types
    return ComplianceRulesSchema(
        rules=[],
        required_sections=[],
        materiality_threshold="Not specified",
    )
