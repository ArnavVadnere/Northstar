export interface Finding {
  id: string;
  severity: "critical" | "high" | "medium" | "low";
  regulation: string;
  issue: string;
  remediation: string;
}

export interface AuditResult {
  audit_id: string;
  timestamp: string;
  company_name: string;
  document_name: string;
  compliance_score: number;
  status: "completed" | "processing" | "failed";
  executive_summary: string;
  findings: Finding[];
  regulations_checked: string[];
}
