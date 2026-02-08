import { AuditResult, AuditHistoryItem } from "./types";

export const mockAuditResult: AuditResult = {
  audit_id: "aud_abc123",
  score: 62,
  grade: "C",
  document_name: "sox_404_report.pdf",
  document_type: "SOX 404",
  timestamp: "2026-02-07T14:32:00Z",
  gaps: [
    {
      severity: "critical",
      title: "Missing ITGC Documentation",
      description:
        "No evidence of IT General Controls documentation for financial reporting systems.",
      regulation: "SOX Section 404(a) — COSO Framework CC5.1",
    },
    {
      severity: "high",
      title: "Inadequate Segregation of Duties",
      description:
        "Same personnel responsible for transaction initiation and approval.",
      regulation: "SOX Section 404(b) — PCAOB AS 2201.22",
    },
    {
      severity: "medium",
      title: "No Quarterly Access Review",
      description:
        "Access logs for financial systems not reviewed on a quarterly basis.",
      regulation: "SOX Section 404 — COSO CC6.1",
    },
  ],
  remediation: [
    "Establish and document ITGC controls for all financial reporting systems within 30 days.",
    "Implement role-based access control to enforce segregation of duties.",
    "Schedule quarterly access log reviews with sign-off from compliance officer.",
    "Deploy automated monitoring for privileged account usage.",
    "Conduct a full internal control gap assessment before next reporting period.",
  ],
  executive_summary:
    "The audit identified three compliance gaps in the uploaded SOX 404 document. A critical deficiency was found in ITGC documentation, with additional high-severity issues in segregation of duties and medium-severity gaps in access review procedures. Immediate remediation is recommended for the critical finding. Overall compliance posture requires significant improvement before the next reporting cycle.",
  report_pdf_url: "/api/files/report_aud_abc123.pdf",
};

export const mockHistory: AuditHistoryItem[] = [
  {
    audit_id: "aud_abc123",
    document_name: "sox_404_report.pdf",
    document_type: "SOX 404",
    score: 62,
    grade: "C",
    timestamp: "2026-02-07T14:32:00Z",
  },
  {
    audit_id: "aud_def456",
    document_name: "annual_report_2025.pdf",
    document_type: "10-K",
    score: 85,
    grade: "B",
    timestamp: "2026-02-05T09:15:00Z",
  },
  {
    audit_id: "aud_ghi789",
    document_name: "material_event_jan.pdf",
    document_type: "8-K",
    score: 91,
    grade: "A",
    timestamp: "2026-01-28T16:45:00Z",
  },
];
