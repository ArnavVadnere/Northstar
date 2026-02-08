# Financial Compliance Auditor API Contract

**Version:** 1.0  
**Last Updated:** 2026-02-07  
**Owner:** Person 2 (Backend)

This document defines the shared API contract between all team members. Person 1 (Discord bot) and Person 3 (Next.js frontend) should build against these endpoints.

---

## Base URL

- **Local Development:** `http://localhost:8000`
- **Production:** TBD

---

## Endpoints

### POST `/api/run-audit`

Runs a compliance audit on an uploaded PDF document.

> [!NOTE]
> This endpoint triggers a 3-agent pipeline (Research -> Analyze -> Report).
> Processing may take 10-30 seconds depending on the PDF size and analysis complexity.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | PDF file upload |
| `document_type` | string | Yes | One of: `"SOX 404"` \| `"10-K"` \| `"8-K"` \| `"Invoice"` |
| `user_id` | string | Yes | Discord user ID or web session ID |

**Response:** `200 OK`

```json
{
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
      "regulation": "SOX Section 404(a) — COSO Framework CC5.1"
    },
    {
      "severity": "high",
      "title": "Inadequate Segregation of Duties",
      "description": "Same personnel responsible for transaction initiation and approval.",
      "regulation": "SOX Section 404(b) — PCAOB AS 2201.22"
    },
    {
      "severity": "medium",
      "title": "No Quarterly Access Review",
      "description": "Access logs for financial systems not reviewed on a quarterly basis.",
      "regulation": "SOX Section 404 — COSO CC6.1"
    }
  ],
  "remediation": [
    "Establish and document ITGC controls for all financial reporting systems within 30 days.",
    "Implement role-based access control to enforce segregation of duties.",
    "Schedule quarterly access log reviews with sign-off from compliance officer.",
    "Deploy automated monitoring for privileged account usage.",
    "Conduct a full internal control gap assessment before next reporting period."
  ],
  "executive_summary": "The audit identified three compliance gaps in the uploaded SOX 404 document. A critical deficiency was found in ITGC documentation, with additional high-severity issues in segregation of duties and medium-severity gaps in access review procedures. Immediate remediation is recommended for the critical finding. Overall compliance posture requires significant improvement before the next reporting cycle. Key risk areas should be incorporated into the organization's ongoing compliance monitoring program.",
  "report_pdf_url": "/api/files/report_aud_abc123.pdf"
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `audit_id` | string | Unique identifier, prefixed with `aud_` |
| `score` | integer | Compliance score 0-100 |
| `grade` | string | Letter grade: `"A"` (90+), `"B"` (80-89), `"C"` (70-79), `"D"` (60-69), `"F"` (<60) |
| `document_name` | string | Original filename of uploaded PDF |
| `document_type` | string | Document type as submitted |
| `timestamp` | string | ISO 8601 timestamp |
| `gaps` | array | 1-5 compliance gaps found (count varies by document quality) |
| `gaps[].severity` | string | One of: `"critical"`, `"high"`, `"medium"` |
| `gaps[].title` | string | Short title of the gap |
| `gaps[].description` | string | Detailed description |
| `gaps[].regulation` | string | Specific regulation reference |
| `remediation` | array | List of 5 remediation steps (strings) |
| `executive_summary` | string | 5-sentence C-suite summary |
| `report_pdf_url` | string | Relative URL to download generated PDF report |

---

### GET `/api/history?user_id={user_id}`

Returns audit history for a specific user.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Discord user ID or web session ID |

**Response:** `200 OK`

```json
{
  "audits": [
    {
      "audit_id": "aud_abc123",
      "document_name": "sox_404_report.pdf",
      "document_type": "SOX 404",
      "score": 62,
      "grade": "C",
      "timestamp": "2026-02-07T14:32:00Z"
    }
  ]
}
```

---

### GET `/api/audit/{audit_id}`

Returns full details of a specific audit.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audit_id` | string | Yes | Audit ID (e.g., `aud_abc123`) |

**Response:** `200 OK`

Same shape as the POST `/api/run-audit` response (full audit detail).

**Error Responses:**

| Status | Description |
|--------|-------------|
| `404 Not Found` | `{"detail": "Audit not found"}` |

---

### GET `/api/files/{filename}`

Returns stored PDF files (generated reports).

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filename` | string | Yes | Filename (e.g., `report_aud_abc123.pdf`) |

**Response:** `200 OK`

- Content-Type: `application/pdf`
- Body: PDF file binary

**Error Responses:**

| Status | Description |
|--------|-------------|
| `404 Not Found` | `{"detail": "File not found"}` |

---

### GET `/api/health`

Health check endpoint for uptime monitoring.

**Response:** `200 OK`

```json
{
  "status": "ok"
}
```

---

## Data Types

### Severity Levels

| Value | Color (for UI) | Description |
|-------|----------------|-------------|
| `critical` | Red | Immediate action required |
| `high` | Orange | High priority |
| `medium` | Yellow | Should be addressed |

### Document Types

| Value | Description |
|-------|-------------|
| `SOX 404` | Sarbanes-Oxley Section 404 internal controls |
| `10-K` | SEC annual report |
| `8-K` | SEC current report (material events) |
| `Invoice` | Financial invoice document |

### Grade Scale

| Score Range | Grade |
|-------------|-------|
| 90-100 | A |
| 80-89 | B |
| 70-79 | C |
| 60-69 | D |
| 0-59 | F |

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## CORS

CORS is enabled for all origins (`*`) during hackathon development.

---

## Notes for Teammates

### Person 1 (Discord Bot)
- Call POST `/api/run-audit` with the PDF file attachment
- Format the JSON response as Discord rich embeds
- Severity colors: critical=red, high=orange, medium=yellow
- Download the PDF report from `report_pdf_url` and attach to message

### Person 3 (Next.js Frontend)
- Use `multipart/form-data` for file uploads
- Poll or await the POST response (processing may take up to 90 seconds)
- Use React Query for caching and state management
- The `report_pdf_url` is relative - prepend the base URL
