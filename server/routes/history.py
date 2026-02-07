"""
History endpoints - GET /api/history, GET /api/audit/{audit_id}
Uses Supabase for data retrieval when configured, falls back to mock data
"""
from fastapi import APIRouter, HTTPException, Query
import os

from db.database import get_history as db_get_history, get_audit as db_get_audit

router = APIRouter()

# Check if Supabase is configured
def is_db_configured() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


# Mock audit data (fallback when DB not configured)
MOCK_AUDITS = {
    "aud_abc123": {
        "audit_id": "aud_abc123",
        "score": 62,
        "grade": "C",
        "document_name": "sox_404_report.pdf",
        "document_type": "SOX 404",
        "timestamp": "2026-02-07T14:32:00Z",
        "gaps": [
            {
                "severity": "critical",
                "title": "Missing ITGC Documentation",
                "description": "No evidence of IT General Controls documentation for financial reporting systems.",
                "regulation": "SOX Section 404(a) — COSO Framework CC5.1",
                "locations": [
                    {
                        "page": 3,
                        "quote": "The company maintains financial reporting systems managed by the IT department",
                        "context": "Section 2.1 - Internal Controls Overview"
                    }
                ]
            },
            {
                "severity": "high",
                "title": "Inadequate Segregation of Duties",
                "description": "Same personnel responsible for transaction initiation and approval.",
                "regulation": "SOX Section 404(b) — PCAOB AS 2201.22",
                "locations": [
                    {
                        "page": 5,
                        "quote": "Transaction processing is handled by the accounting team",
                        "context": "Section 3.2 - Transaction Controls"
                    },
                    {
                        "page": 7,
                        "quote": "Approvals are conducted by department managers",
                        "context": "Section 4.1 - Approval Workflow"
                    }
                ]
            },
            {
                "severity": "medium",
                "title": "No Quarterly Access Review",
                "description": "Access logs for financial systems not reviewed on a quarterly basis.",
                "regulation": "SOX Section 404 — COSO CC6.1",
                "locations": [
                    {
                        "page": 8,
                        "quote": "System access is reviewed on an annual basis",
                        "context": "Section 5.1 - Access Management"
                    }
                ]
            }
        ],
        "remediation": [
            "Establish and document ITGC controls for all financial reporting systems within 30 days.",
            "Implement role-based access control to enforce segregation of duties.",
            "Schedule quarterly access log reviews with sign-off from compliance officer.",
            "Deploy automated monitoring for privileged account usage.",
            "Conduct a full internal control gap assessment before next reporting period."
        ],
        "executive_summary": "The audit identified three compliance gaps in the uploaded SOX 404 document. A critical deficiency was found in ITGC documentation, with additional high-severity issues in segregation of duties and medium-severity gaps in access review procedures. Immediate remediation is recommended for the critical finding. Overall compliance posture requires significant improvement before the next reporting cycle.",
        "report_pdf_url": "/api/files/report_aud_abc123.pdf"
    },
    "aud_def456": {
        "audit_id": "aud_def456",
        "score": 78,
        "grade": "B",
        "document_name": "10k_q3_2025.pdf",
        "document_type": "10-K",
        "timestamp": "2026-02-07T13:10:00Z",
        "gaps": [
            {
                "severity": "high",
                "title": "Risk Factor Disclosure Gap",
                "description": "Emerging cybersecurity risks not adequately disclosed in risk factors section.",
                "regulation": "SEC Regulation S-K Item 105",
                "locations": [
                    {
                        "page": 12,
                        "quote": "The company faces various operational risks",
                        "context": "Item 1A - Risk Factors"
                    }
                ]
            },
            {
                "severity": "medium",
                "title": "MD&A Forward-Looking Statements",
                "description": "Forward-looking statements lack sufficient cautionary language.",
                "regulation": "SEC Regulation S-K Item 303",
                "locations": [
                    {
                        "page": 25,
                        "quote": "We expect continued growth in the coming fiscal year",
                        "context": "Item 7 - MD&A"
                    }
                ]
            },
            {
                "severity": "medium",
                "title": "Executive Compensation Disclosure",
                "description": "Performance metrics for executive bonuses not fully disclosed.",
                "regulation": "SEC Regulation S-K Item 402",
                "locations": [
                    {
                        "page": 45,
                        "quote": "Executive compensation is tied to company performance",
                        "context": "Item 11 - Executive Compensation"
                    }
                ]
            }
        ],
        "remediation": [
            "Update risk factors to include detailed cybersecurity risk disclosures.",
            "Add safe harbor language to all forward-looking statements in MD&A.",
            "Disclose specific performance metrics and thresholds for executive compensation.",
            "Conduct a full disclosure controls assessment before next filing.",
            "Engage external counsel to review disclosure adequacy."
        ],
        "executive_summary": "The 10-K filing audit identified three compliance gaps. A high-severity issue was found in risk factor disclosures regarding cybersecurity. Medium-severity gaps exist in forward-looking statement cautionary language and executive compensation disclosure. Overall compliance posture is good but requires targeted improvements before the next annual filing.",
        "report_pdf_url": "/api/files/report_aud_def456.pdf"
    }
}


@router.get("/history")
async def get_history(user_id: str = Query(..., description="Discord user ID or web session ID")):
    """
    Get audit history for a specific user.
    
    Uses Supabase if configured, otherwise returns mock data.
    """
    if is_db_configured():
        try:
            audits = await db_get_history(user_id)
            return {"audits": audits}
        except Exception as e:
            print(f"Warning: Failed to fetch history from database: {e}")
            # Fall through to mock data
    
    # Return mock data
    mock_audits = [
        {
            "audit_id": audit["audit_id"],
            "document_name": audit["document_name"],
            "document_type": audit["document_type"],
            "score": audit["score"],
            "grade": audit["grade"],
            "timestamp": audit["timestamp"]
        }
        for audit in MOCK_AUDITS.values()
    ]
    
    return {"audits": mock_audits}


@router.get("/audit/{audit_id}")
async def get_audit(audit_id: str):
    """
    Get full details of a specific audit.
    
    Uses Supabase if configured, otherwise returns mock data.
    """
    if is_db_configured():
        try:
            audit = await db_get_audit(audit_id)
            if audit:
                return audit
            # If not found in DB, fall through to check mock data
        except Exception as e:
            print(f"Warning: Failed to fetch audit from database: {e}")
            # Fall through to mock data
    
    # Check mock data
    if audit_id not in MOCK_AUDITS:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return MOCK_AUDITS[audit_id]
