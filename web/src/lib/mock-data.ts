import { AuditResult } from "./types";

export const mockAudits: AuditResult[] = [
  {
    audit_id: "aud-001",
    timestamp: "2026-02-05T14:30:00Z",
    company_name: "Acme Financial Corp",
    document_name: "Q4_2025_Financial_Report.pdf",
    compliance_score: 72,
    status: "completed",
    executive_summary:
      "The document demonstrates partial compliance with SOX and PCI-DSS regulations. Critical gaps were identified in internal control documentation and data encryption standards. Immediate remediation is recommended for 3 critical findings.",
    findings: [
      {
        id: "f-001",
        severity: "critical",
        regulation: "SOX Section 404",
        issue: "Missing internal control assessment over financial reporting",
        remediation:
          "Document and test all internal controls over financial reporting. Engage external auditor to validate control effectiveness.",
      },
      {
        id: "f-002",
        severity: "high",
        regulation: "PCI-DSS Req 3.4",
        issue: "Cardholder data stored without encryption at rest",
        remediation:
          "Implement AES-256 encryption for all stored cardholder data. Deploy key management procedures per PCI-DSS Requirement 3.5.",
      },
      {
        id: "f-003",
        severity: "medium",
        regulation: "SOX Section 302",
        issue: "CEO/CFO certification procedures not fully documented",
        remediation:
          "Create formal certification checklist and sign-off procedures for quarterly and annual reports.",
      },
      {
        id: "f-004",
        severity: "low",
        regulation: "PCI-DSS Req 12.6",
        issue: "Security awareness training records incomplete",
        remediation:
          "Update training records to include completion dates and quiz scores for all employees.",
      },
    ],
    regulations_checked: ["SOX", "PCI-DSS"],
  },
  {
    audit_id: "aud-002",
    timestamp: "2026-02-03T09:15:00Z",
    company_name: "HealthFirst Inc",
    document_name: "Patient_Data_Policy_2026.pdf",
    compliance_score: 45,
    status: "completed",
    executive_summary:
      "Significant compliance gaps identified across HIPAA and GDPR requirements. The document lacks critical data protection provisions and breach notification procedures. Urgent remediation required.",
    findings: [
      {
        id: "f-005",
        severity: "critical",
        regulation: "HIPAA §164.312",
        issue: "No technical safeguards for electronic protected health information (ePHI)",
        remediation:
          "Implement access controls, audit controls, integrity controls, and transmission security for all ePHI systems.",
      },
      {
        id: "f-006",
        severity: "critical",
        regulation: "GDPR Article 33",
        issue: "Breach notification procedure missing entirely",
        remediation:
          "Establish a 72-hour breach notification procedure with templates for supervisory authority and data subject notifications.",
      },
      {
        id: "f-007",
        severity: "high",
        regulation: "HIPAA §164.308",
        issue: "Risk analysis not conducted in the past 12 months",
        remediation:
          "Conduct comprehensive risk analysis covering all ePHI assets, threats, and vulnerabilities. Document mitigation plans.",
      },
    ],
    regulations_checked: ["HIPAA", "GDPR"],
  },
  {
    audit_id: "aud-003",
    timestamp: "2026-01-28T16:45:00Z",
    company_name: "Global Bank Ltd",
    document_name: "Risk_Management_Framework.pdf",
    compliance_score: 91,
    status: "completed",
    executive_summary:
      "Strong compliance posture across Basel III and SOX requirements. Minor documentation gaps identified. The organization demonstrates mature risk management practices with only minor improvements needed.",
    findings: [
      {
        id: "f-008",
        severity: "low",
        regulation: "Basel III Pillar 3",
        issue: "Disclosure frequency could be improved from annual to semi-annual",
        remediation:
          "Increase public disclosure frequency to semi-annual to align with best practices.",
      },
      {
        id: "f-009",
        severity: "medium",
        regulation: "SOX Section 404",
        issue: "Minor gaps in IT general controls documentation",
        remediation:
          "Update IT general controls documentation to include change management and access provisioning procedures.",
      },
    ],
    regulations_checked: ["Basel III", "SOX"],
  },
];
