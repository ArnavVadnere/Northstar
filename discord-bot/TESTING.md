# Testing Guide

## Local Testing

1. Set up a test Discord server
2. Create a bot application at https://discord.com/developers/applications
3. Copy bot token to `.env`
4. Enable **Message Content** intent in the bot settings
5. Invite bot to test server with `bot` + `applications.commands` scopes
6. Run `python bot.py`

## Mock Testing (Without Backend)

To test the bot without the FastAPI backend running, modify `services/api_client.py` to return mock responses. Replace the method bodies with:

```python
async def run_audit(self, user_id, pdf_bytes, filename, document_type):
    return {
        "audit_id": "aud_test123",
        "score": 62,
        "grade": "C",
        "document_name": filename,
        "document_type": document_type,
        "timestamp": "2026-02-07T14:32:00Z",
        "gaps": [
            {
                "severity": "critical",
                "title": "Missing Risk Factors Section",
                "description": "Item 1A risk disclosures not found",
                "regulation": "SEC Reg S-K Item 1A"
            },
            {
                "severity": "high",
                "title": "Incomplete MD&A",
                "description": "Management discussion lacks forward-looking statements",
                "regulation": "SEC Reg S-K Item 7"
            },
            {
                "severity": "medium",
                "title": "XBRL Tagging Gaps",
                "description": "Several financial line items missing iXBRL tags",
                "regulation": "SEC Rule 405 Reg S-T"
            }
        ],
        "remediation": [
            "Add comprehensive risk factors section covering market, operational, and regulatory risks",
            "Expand MD&A with forward-looking statements and quantitative disclosures",
            "Complete iXBRL tagging for all financial statement line items",
            "Include controls and procedures attestation from management",
            "Add auditor's report with going concern assessment"
        ],
        "executive_summary": "The document received a compliance score of 62/100 (Grade C). Critical gaps were identified in risk factor disclosures and MD&A completeness. The filing lacks required XBRL tagging for several financial items. Immediate remediation is recommended before submission. Overall, the document requires significant revision to meet 2026 SEC requirements.",
        "report_pdf_url": "/api/files/report_aud_test123.pdf"
    }

async def get_history(self, user_id):
    return {
        "audits": [
            {
                "audit_id": "aud_test123",
                "document_name": "sox_404_report.pdf",
                "document_type": "SOX 404",
                "score": 62,
                "grade": "C",
                "timestamp": "2026-02-07T14:32:00Z"
            },
            {
                "audit_id": "aud_test456",
                "document_name": "10k_annual.pdf",
                "document_type": "10-K",
                "score": 85,
                "grade": "B",
                "timestamp": "2026-02-07T10:15:00Z"
            }
        ]
    }

async def get_audit_detail(self, audit_id):
    # Return same shape as run_audit mock
    return await self.run_audit("mock", b"", "mock.pdf", "10-K")

async def download_pdf(self, report_url):
    return None  # Skip PDF attachment in mock mode
```

## Test Cases

- [ ] `/audit` with valid PDF — should show processing embed, then result embed
- [ ] `/audit` with non-PDF file (e.g. .txt) — should show "Please upload a PDF file" error
- [ ] `/audit` with >50MB file — should show "File must be under 50 MB" error
- [ ] `/history` with no audits — should show "You haven't run any audits yet" message
- [ ] `/history` with multiple audits — should show history embed with scores and dates
- [ ] `/audit-detail` with valid audit_id — should show detailed embed with all gaps and remediation
- [ ] `/audit-detail` with invalid audit_id — should show "No audit found" error
- [ ] API timeout scenario — should show timeout message
- [ ] API error response (500) — should show generic error message
- [ ] Embed colour matches grade (A=green, B=blue, C=yellow, D=orange, F=red)
