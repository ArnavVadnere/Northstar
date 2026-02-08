import { AuditResult, AuditHistoryItem } from "./types";
import { mockAuditResult, mockHistory } from "./mock-data";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

/**
 * POST /api/run-audit
 * Submit a document for compliance audit.
 */
export async function runAudit(
  file: File,
  documentType: string,
  userId: string
): Promise<AuditResult> {
  if (!API_BASE) {
    await new Promise((r) => setTimeout(r, 2000));
    return mockAuditResult;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("document_type", documentType);
  formData.append("user_id", userId);

  const res = await fetch(`${API_BASE}/api/run-audit`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Audit failed" }));
    const detail = err.detail;

    // Backend returns detail as a string for simple validation errors
    // and as an object { error_code, message } for pipeline validation errors.
    if (typeof detail === "object" && detail !== null) {
      throw new Error(detail.message || "Audit validation failed");
    }
    throw new Error(detail || `Audit submission failed: ${res.status}`);
  }

  return res.json();
}

/**
 * GET /api/audit/:audit_id
 * Fetch a single audit result by ID.
 */
export async function getAuditResult(auditId: string): Promise<AuditResult> {
  if (!API_BASE) {
    await new Promise((r) => setTimeout(r, 500));
    if (auditId === mockAuditResult.audit_id) return mockAuditResult;
    throw new Error("Audit not found");
  }

  const res = await fetch(`${API_BASE}/api/audit/${auditId}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Audit not found: ${res.status}`);
  }

  return res.json();
}

/**
 * GET /api/history?user_id=...
 * Fetch audit history for a user.
 */
export async function getAuditHistory(
  userId: string = "web-user"
): Promise<AuditHistoryItem[]> {
  if (!API_BASE) {
    await new Promise((r) => setTimeout(r, 300));
    return mockHistory;
  }

  const res = await fetch(
    `${API_BASE}/api/history?user_id=${encodeURIComponent(userId)}`,
    { cache: "no-store" }
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch history: ${res.status}`);
  }

  const data = await res.json();
  return data.audits;
}

/**
 * Build full URL for report PDF download.
 */
export function getReportPdfUrl(relativePath: string): string {
  const base = API_BASE || "http://localhost:8000";
  return `${base}${relativePath}`;
}
