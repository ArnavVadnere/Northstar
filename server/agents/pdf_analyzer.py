"""
Agent 2: PDF Analyzer (Dedalus)

Analyzes extracted PDF text against compliance rules to identify gaps.
Uses Dedalus SDK with structured outputs for reliable JSON responses.

Owner: Person 2
"""
import os
import base64
from typing import Optional, List
from pydantic import BaseModel
from dedalus_labs import AsyncDedalus, DedalusRunner
import json
import logging
import re
from dotenv import load_dotenv

load_dotenv()

# Enable verbose logging for Dedalus/LangChain
logging.basicConfig(level=logging.INFO)
# logging.getLogger("dedalus_labs").setLevel(logging.DEBUG)  # Use DEBUG for more detail


# --- Pydantic models for structured output ---

class ComplianceGap(BaseModel):
    """A single compliance gap identified in the document."""
    severity: str  # 'critical', 'high', 'medium'
    title: str
    description: str
    regulation: str


class AnalysisResult(BaseModel):
    """Structured result from the PDF analyzer agent."""
    gaps: List[ComplianceGap]


# --- Compliance rules by document type ---

COMPLIANCE_RULES = {
    "SOX 404": """
SOX 404 Compliance Requirements (Sarbanes-Oxley Section 404):

1. ITGC (IT General Controls) - SOX Section 404(a), COSO Framework CC5.1
   - Must document IT controls for all financial reporting systems
   - Must have change management procedures
   - Must have access controls and logging

2. Segregation of Duties - SOX Section 404(b), PCAOB AS 2201.22
   - Transaction initiators cannot be approvers
   - Separation between accounting and custody functions
   - Independent reconciliation required

3. Access Reviews - SOX Section 404, COSO CC6.1
   - Quarterly access reviews required
   - Privileged access monitoring
   - Timely access revocation for terminated employees

4. Documentation Requirements
   - Risk assessment documentation
   - Control testing evidence
   - Management sign-off on control effectiveness

5. Financial Close Controls
   - Account reconciliation procedures
   - Journal entry review process
   - Period-end close timeline compliance
""",
    "10-K": """
SEC 10-K Filing Compliance Requirements:

1. Risk Factor Disclosures - SEC Regulation S-K Item 105
   - Material risks must be disclosed
   - Cybersecurity risks (if material)
   - Industry-specific risks
   - Economic and market risks

2. MD&A Requirements - SEC Regulation S-K Item 303
   - Liquidity and capital resources discussion
   - Results of operations analysis
   - Forward-looking statements with safe harbor language
   - Critical accounting estimates

3. Executive Compensation - SEC Regulation S-K Item 402
   - Compensation discussion and analysis
   - Performance metrics disclosure
   - Benchmarking disclosure
   - Perquisites and benefits disclosure

4. Financial Statement Compliance
   - GAAP conformity
   - Auditor's report inclusion
   - Management's internal control report

5. Exhibit Requirements
   - Material contracts
   - Certifications (302, 906)
   - Subsidiary list
""",
    "8-K": """
SEC 8-K Current Report Compliance Requirements:

1. Timely Disclosure - SEC Rule 13a-11
   - Must file within 4 business days of triggering events
   - Material events require immediate disclosure

2. Triggering Events Disclosure
   - Entry into material agreements (Item 1.01)
   - Bankruptcy or receivership (Item 1.03)
   - Material business operations changes (Item 2.01)
   - Financial obligation creation (Item 2.03)
   - Triggering events list complete

3. Financial Statements - Item 9.01
   - Pro forma financials if required
   - Acquired company financials if acquisition
   - Exhibit compliance

4. Officer Changes - Item 5.02
   - Departure of directors/officers
   - Appointment of officers
   - Compensation arrangements
""",
    "Invoice": """
Invoice Compliance Requirements:

1. Invoice Documentation Standards
   - Unique invoice number required
   - Date of issue clearly stated
   - Vendor/supplier identification
   - Purchase order reference

2. Tax Compliance
   - Tax identification numbers
   - Applicable tax rates
   - Tax exemption documentation if claimed

3. Payment Terms
   - Clear payment due date
   - Accepted payment methods
   - Late payment penalties disclosed

4. Approval Workflow
   - Authorized approver signature/system
   - Budget code/cost center
   - Three-way match documentation (PO, receipt, invoice)
"""
}


def _extract_json(text: str) -> str:
    """Strip markdown code fences from LLM JSON output."""
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if match:
        return match.group(1).strip()
    return text.strip()



async def analyze_pdf(
    extracted_text: dict,
    document_type: str,
    compliance_rules: Optional[str] = None,
    pdf_bytes: Optional[bytes] = None,
) -> AnalysisResult:
    """
    Analyze extracted PDF text against compliance rules using Dedalus.

    Args:
        extracted_text: Output from pdf_extractor (contains full_text and pages)
        document_type: Type of document ('SOX 404', '10-K', '8-K', 'Invoice')
        compliance_rules: Optional custom rules (defaults to built-in rules)
        pdf_bytes: Raw PDF bytes for MCP tool usage (extract_tables)

    Returns:
        AnalysisResult with identified gaps and locations
    """
    # Get compliance rules
    rules = compliance_rules or COMPLIANCE_RULES.get(document_type, "")
    if not rules:
        rules = "General financial document compliance standards apply."

    doc_text = extracted_text.get("full_text", "")

    # Base64-encode PDF bytes for MCP tools that need url_or_bytes
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8") if pdf_bytes else None

    # Select relevant MCP tools per document type to minimize tool calls
    TOOLS_BY_DOCTYPE = {
        "SOX 404": [
            ("find_regulatory_sections", f"pdf_path={{PDF_B64}}, doc_type='{document_type}'"),
            ("detect_compliance_red_flags", "pdf_path={PDF_B64}"),
            ("check_required_signatures", "pdf_path={PDF_B64}"),
        ],
        "10-K": [
            ("find_regulatory_sections", f"pdf_path={{PDF_B64}}, doc_type='{document_type}'"),
            ("extract_financial_statements", "pdf_path={PDF_B64}"),
            ("detect_compliance_red_flags", "pdf_path={PDF_B64}"),
        ],
        "8-K": [
            ("find_regulatory_sections", f"pdf_path={{PDF_B64}}, doc_type='{document_type}'"),
            ("detect_compliance_red_flags", "pdf_path={PDF_B64}"),
        ],
        "Invoice": [
            ("validate_financial_math", "pdf_path={PDF_B64}"),
            ("check_required_signatures", "pdf_path={PDF_B64}"),
        ],
    }
    selected_tools = TOOLS_BY_DOCTYPE.get(document_type, [
        ("find_regulatory_sections", f"pdf_path={{PDF_B64}}, doc_type='{document_type}'"),
        ("detect_compliance_red_flags", "pdf_path={PDF_B64}"),
    ])

    # Build the MCP tool instruction block
    tool_lines = "\n".join(
        f"{i+1}. Call `{name}` with {args}"
        for i, (name, args) in enumerate(selected_tools)
    )
    mcp_instructions = f"""
IMPORTANT — MCP TOOL USAGE:
You have access to MCP tools from the legal-doc-mcp server. Call these tools in order:

{tool_lines}

Use the outputs from these tool calls to inform your compliance gap analysis.
If a tool call fails or returns empty results, proceed with the raw text provided.
"""
    if pdf_b64:
        mcp_instructions += f"""
Where {{PDF_B64}} appears above, use this exact base64 string as the pdf_path value:
{pdf_b64}
"""

    # Create the analysis prompt
    prompt = f"""You are a compliance analyst reviewing a {document_type} document.
{mcp_instructions}
DOCUMENT TEXT (for reference):
---
{doc_text}
---

COMPLIANCE RULES TO CHECK AGAINST:
{rules}

TASK:
First, call the MCP tools listed above (in order).
Then, analyze this document against the compliance rules. For each compliance gap you find:
1. Identify the severity (critical, high, or medium)
2. Give it a clear, specific title
3. Provide a detailed description of what's missing or non-compliant
4. Reference the specific regulation it violates

Focus on finding real gaps based on what's actually in (or missing from) the document.
If the document is very short or lacks substantive content, note that as a gap itself.

Identify all genuine compliance gaps you find. Assign each gap a severity:
- "critical": Immediate regulatory risk or material deficiency
- "high": Significant gap requiring prompt remediation
- "medium": Notable issue that should be addressed

Only report gaps that are genuinely present — do not invent gaps to fill a quota.
If the document is largely compliant, it is acceptable to return fewer gaps.
Return between 1 and 5 gaps.

Provide your analysis as structured JSON with the following format:
{{
  "gaps": [
    {{
      "severity": "critical|high|medium",
      "title": "Short descriptive title",
      "description": "Detailed explanation of the compliance gap",
      "regulation": "Specific regulation reference"
    }}
  ]
}}"""

    # Check if Dedalus is configured
    if not os.getenv("DEDALUS_API_KEY"):
        return _mock_analysis(document_type, "DEDALUS_API_KEY not set")
    
    try:
        client = AsyncDedalus(timeout=300)  # 5 minutes for MCP PDF processing
        runner = DedalusRunner(client)
        
        print(f"[Agent 2] >>> Starting compliance analysis...")

        result = await runner.run(
            input=prompt,
            model="openai/gpt-4o",
            max_steps=len(selected_tools) + 2,
            mcp_servers=["sdas04/legal-doc-mcp"],
        )

        print(f"[Agent 2] >>> SUCCESS: Analysis completed using Dedalus")
        print(f"[Agent 2] MCP results: {getattr(result, 'mcp_results', [])}")
        print(f"[Agent 2] Steps used: {getattr(result, 'steps_used', 'N/A')}")

        # Parse the response
        if hasattr(result, 'final_output') and result.final_output:
            # If we got structured output, it should already be an AnalysisResult
            if isinstance(result.final_output, AnalysisResult):
                return result.final_output
            
            # Otherwise try to parse it
            try:
                cleaned = _extract_json(result.final_output)
                data = json.loads(cleaned)
                return AnalysisResult(**data)
            except (json.JSONDecodeError, TypeError):
                # Fallback: use mock data
                return _mock_analysis(document_type)
        
        return _mock_analysis(document_type)
        
    except Exception as e:
        print(f"[Agent 2] >>> ERROR: Dedalus analysis failed: {e}")
        return _mock_analysis(document_type, f"Dedalus error: {str(e)}")


def _mock_analysis(document_type: str, reason: str = "Dedalus service unavailable") -> AnalysisResult:
    """Return mock analysis when Dedalus is not available or fails."""

    print(f"[Agent 2] NOTICE: Using fallback mock data. Reason: {reason}")

    if document_type == "SOX 404":
        return AnalysisResult(
            gaps=[
                ComplianceGap(
                    severity="critical",
                    title="Missing ITGC Documentation",
                    description="No evidence of IT General Controls documentation for financial reporting systems.",
                    regulation="SOX Section 404(a) — COSO Framework CC5.1"
                ),
                ComplianceGap(
                    severity="high",
                    title="Inadequate Segregation of Duties",
                    description="Same personnel responsible for transaction initiation and approval.",
                    regulation="SOX Section 404(b) — PCAOB AS 2201.22"
                ),
                ComplianceGap(
                    severity="medium",
                    title="No Quarterly Access Review",
                    description="Access logs for financial systems not reviewed on a quarterly basis.",
                    regulation="SOX Section 404 — COSO CC6.1"
                )
            ]
        )
    elif document_type in ["10-K", "8-K"]:
        return AnalysisResult(
            gaps=[
                ComplianceGap(
                    severity="critical",
                    title="Risk Factor Disclosure Gap",
                    description="Material risks not adequately disclosed in risk factors section.",
                    regulation="SEC Regulation S-K Item 105"
                ),
                ComplianceGap(
                    severity="high",
                    title="Forward-Looking Statements",
                    description="Forward-looking statements lack sufficient cautionary language.",
                    regulation="SEC Regulation S-K Item 303"
                ),
                ComplianceGap(
                    severity="medium",
                    title="Executive Compensation Disclosure",
                    description="Performance metrics for compensation not fully disclosed.",
                    regulation="SEC Regulation S-K Item 402"
                )
            ]
        )
    else:
        return AnalysisResult(
            gaps=[
                ComplianceGap(
                    severity="critical",
                    title="Documentation Gap",
                    description="Required documentation elements are missing or incomplete.",
                    regulation="General compliance standards"
                ),
                ComplianceGap(
                    severity="high",
                    title="Approval Workflow Missing",
                    description="No evidence of proper approval workflow.",
                    regulation="Internal control standards"
                ),
                ComplianceGap(
                    severity="medium",
                    title="Tax Compliance Gap",
                    description="Tax identification numbers and applicable tax rates not documented.",
                    regulation="Tax compliance standards"
                )
            ]
        )
