export interface ComplianceGap {
  severity: "critical" | "high" | "medium";
  title: string;
  description: string;
  regulation: string;
}

export interface AuditResult {
  audit_id: string;
  score: number;
  grade: string;
  document_name: string;
  document_type: string;
  timestamp: string;
  gaps: ComplianceGap[];
  remediation: string[];
  executive_summary: string;
  report_pdf_url: string;
}

export interface AuditHistoryItem {
  audit_id: string;
  document_name: string;
  document_type: string;
  score: number;
  grade: string;
  timestamp: string;
}
