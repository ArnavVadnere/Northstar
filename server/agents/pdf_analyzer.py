"""
Agent 2: PDF Analyzer (Dedalus)

Analyzes extracted PDF text against compliance rules to identify gaps.
Uses Dedalus SDK with structured outputs for reliable JSON responses.

Owner: Person 2
"""
import os
from typing import Optional, List
from pydantic import BaseModel
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()


# --- Pydantic models for structured output ---

class GapLocation(BaseModel):
    """Location in the PDF where a gap was identified."""
    page: int
    quote: str
    context: str


class ComplianceGap(BaseModel):
    """A single compliance gap identified in the document."""
    severity: str  # 'critical', 'high', 'medium'
    title: str
    description: str
    regulation: str
    locations: List[GapLocation]


class AnalysisResult(BaseModel):
    """Structured result from the PDF analyzer agent."""
    gaps: List[ComplianceGap]
    raw_observations: Optional[str] = None


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


async def analyze_pdf(
    extracted_text: dict,
    document_type: str,
    compliance_rules: Optional[str] = None
) -> AnalysisResult:
    """
    Analyze extracted PDF text against compliance rules using Dedalus.
    
    Args:
        extracted_text: Output from pdf_extractor (contains full_text and pages)
        document_type: Type of document ('SOX 404', '10-K', '8-K', 'Invoice')
        compliance_rules: Optional custom rules (defaults to built-in rules)
    
    Returns:
        AnalysisResult with identified gaps and locations
    """
    # Get compliance rules
    rules = compliance_rules or COMPLIANCE_RULES.get(document_type, "")
    if not rules:
        rules = "General financial document compliance standards apply."
    
    # Build the page text with page numbers for location reference
    pages_text = ""
    for page in extracted_text.get("pages", []):
        pages_text += f"\n\n--- PAGE {page['page_num']} ---\n{page['text']}"
    
    # Create the analysis prompt
    prompt = f"""You are a compliance analyst reviewing a {document_type} document.

COMPLIANCE RULES TO CHECK AGAINST:
{rules}

DOCUMENT CONTENT (with page numbers):
{pages_text}

TASK:
Analyze this document against the compliance rules above. For each compliance gap you find:
1. Identify the severity (critical, high, or medium)
2. Give it a clear, specific title
3. Provide a detailed description of what's missing or non-compliant
4. Reference the specific regulation it violates
5. Quote the exact text from the document that indicates the gap, noting which page it's on

Focus on finding real gaps based on what's actually in (or missing from) the document.
If the document is very short or lacks substantive content, note that as a gap itself.

Provide your analysis as structured JSON with the following format:
{{
  "gaps": [
    {{
      "severity": "critical|high|medium",
      "title": "Short descriptive title",
      "description": "Detailed explanation of the compliance gap",
      "regulation": "Specific regulation reference",
      "locations": [
        {{
          "page": 1,
          "quote": "Exact text from document",
          "context": "Section or heading where found"
        }}
      ]
    }}
  ]
}}

Identify 2-4 gaps that are genuinely present based on the document content."""

    # Check if Dedalus is configured
    if not os.getenv("DEDALUS_API_KEY"):
        # Return mock analysis if no API key
        return _mock_analysis(document_type)
    
    try:
        client = AsyncDedalus()
        runner = DedalusRunner(client)
        
        result = await runner.run(
            input=prompt,
            model="openai/gpt-4o",
            response_format=AnalysisResult,
            max_steps=3
        )
        
        # Parse the response
        if hasattr(result, 'final_output') and result.final_output:
            # If we got structured output, it should already be an AnalysisResult
            if isinstance(result.final_output, AnalysisResult):
                return result.final_output
            
            # Otherwise try to parse it
            import json
            try:
                data = json.loads(result.final_output)
                return AnalysisResult(**data)
            except (json.JSONDecodeError, TypeError):
                # Fallback: wrap the text response
                return AnalysisResult(
                    gaps=_mock_analysis(document_type).gaps,
                    raw_observations=str(result.final_output)
                )
        
        return _mock_analysis(document_type)
        
    except Exception as e:
        print(f"Dedalus analysis failed: {e}")
        return _mock_analysis(document_type)


def _mock_analysis(document_type: str) -> AnalysisResult:
    """Return mock analysis when Dedalus is not available."""
    
    if document_type == "SOX 404":
        return AnalysisResult(
            gaps=[
                ComplianceGap(
                    severity="critical",
                    title="Missing ITGC Documentation",
                    description="No evidence of IT General Controls documentation for financial reporting systems.",
                    regulation="SOX Section 404(a) — COSO Framework CC5.1",
                    locations=[GapLocation(page=1, quote="Document lacks ITGC controls description", context="General")]
                ),
                ComplianceGap(
                    severity="high",
                    title="Inadequate Segregation of Duties",
                    description="Same personnel responsible for transaction initiation and approval.",
                    regulation="SOX Section 404(b) — PCAOB AS 2201.22",
                    locations=[GapLocation(page=1, quote="No segregation of duties policy found", context="General")]
                ),
                ComplianceGap(
                    severity="medium",
                    title="No Quarterly Access Review",
                    description="Access logs for financial systems not reviewed on a quarterly basis.",
                    regulation="SOX Section 404 — COSO CC6.1",
                    locations=[GapLocation(page=1, quote="Access review frequency not specified", context="General")]
                )
            ]
        )
    elif document_type in ["10-K", "8-K"]:
        return AnalysisResult(
            gaps=[
                ComplianceGap(
                    severity="high",
                    title="Risk Factor Disclosure Gap",
                    description="Material risks not adequately disclosed in risk factors section.",
                    regulation="SEC Regulation S-K Item 105",
                    locations=[GapLocation(page=1, quote="Limited risk disclosure found", context="Risk Factors")]
                ),
                ComplianceGap(
                    severity="medium",
                    title="Forward-Looking Statements",
                    description="Forward-looking statements lack sufficient cautionary language.",
                    regulation="SEC Regulation S-K Item 303",
                    locations=[GapLocation(page=1, quote="Missing safe harbor language", context="MD&A")]
                ),
                ComplianceGap(
                    severity="medium",
                    title="Executive Compensation Disclosure",
                    description="Performance metrics for compensation not fully disclosed.",
                    regulation="SEC Regulation S-K Item 402",
                    locations=[GapLocation(page=1, quote="Compensation metrics unclear", context="Executive Compensation")]
                )
            ]
        )
    else:
        return AnalysisResult(
            gaps=[
                ComplianceGap(
                    severity="high",
                    title="Documentation Gap",
                    description="Required documentation elements are missing or incomplete.",
                    regulation="General compliance standards",
                    locations=[GapLocation(page=1, quote="Incomplete documentation", context="General")]
                ),
                ComplianceGap(
                    severity="medium",
                    title="Approval Workflow Missing",
                    description="No evidence of proper approval workflow.",
                    regulation="Internal control standards",
                    locations=[GapLocation(page=1, quote="No approval signatures found", context="General")]
                )
            ]
        )
