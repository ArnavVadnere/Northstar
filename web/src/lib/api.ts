import { AuditResult } from "./types";
import { mockAudits } from "./mock-data";

// Replace with Person 2's FastAPI base URL when ready
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Submit a document for compliance audit.
 * Sends file + metadata to Person 2's FastAPI backend.
 */
export async function runAudit(
  file: File,
  companyName: string,
  regulation: string
): Promise<{ audit_id: string }> {
  // --- MOCK: remove this block when backend is ready ---
  if (!process.env.NEXT_PUBLIC_API_URL) {
    await new Promise((r) => setTimeout(r, 1500));
    return { audit_id: "aud-001" };
  }
  // --- END MOCK ---

  const formData = new FormData();
  formData.append("file", file);
  formData.append("company_name", companyName);
  formData.append("regulation", regulation);

  const res = await fetch(`${API_BASE}/audit`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Audit submission failed: ${res.status}`);
  }

  return res.json();
}

/**
 * Fetch a single audit result by ID.
 */
export async function getAuditResult(auditId: string): Promise<AuditResult> {
  // --- MOCK ---
  if (!process.env.NEXT_PUBLIC_API_URL) {
    await new Promise((r) => setTimeout(r, 500));
    const audit = mockAudits.find((a) => a.audit_id === auditId);
    if (!audit) throw new Error("Audit not found");
    return audit;
  }
  // --- END MOCK ---

  const res = await fetch(`${API_BASE}/audit/${auditId}`);

  if (!res.ok) {
    throw new Error(`Failed to fetch audit: ${res.status}`);
  }

  return res.json();
}

/**
 * Fetch all past audit results.
 */
export async function getAuditHistory(): Promise<AuditResult[]> {
  // --- MOCK ---
  if (!process.env.NEXT_PUBLIC_API_URL) {
    await new Promise((r) => setTimeout(r, 300));
    return mockAudits;
  }
  // --- END MOCK ---

  const res = await fetch(`${API_BASE}/audits`);

  if (!res.ok) {
    throw new Error(`Failed to fetch audit history: ${res.status}`);
  }

  return res.json();
}
