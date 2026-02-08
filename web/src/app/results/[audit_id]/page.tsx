"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { getAuditResult, getReportPdfUrl } from "@/lib/api";
import { getCachedAudit } from "@/lib/audit-cache";
import { format } from "date-fns";
import type { AuditResult, ComplianceGap } from "@/lib/types";

const severityStyle: Record<ComplianceGap["severity"], string> = {
  critical: "bg-red-500/15 text-red-400 border-red-500/30",
  high: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  medium: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
};

function scoreColor(score: number) {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-yellow-400";
  return "text-red-400";
}

function progressColor(score: number) {
  if (score >= 80) return "[&>div]:bg-emerald-500";
  if (score >= 60) return "[&>div]:bg-yellow-500";
  return "[&>div]:bg-red-500";
}

function gradeStyle(score: number) {
  if (score >= 80) return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
  if (score >= 60) return "bg-yellow-500/15 text-yellow-400 border-yellow-500/30";
  return "bg-red-500/15 text-red-400 border-red-500/30";
}

export default function ResultsPage() {
  const params = useParams();
  const auditId = params.audit_id as string;

  const [audit, setAudit] = useState<AuditResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const cached = getCachedAudit(auditId);
      if (cached) {
        setAudit(cached);
        setLoading(false);
        return;
      }
      try {
        const result = await getAuditResult(auditId);
        setAudit(result);
      } catch {
        setError("Audit not found.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [auditId]);

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-20 text-center">
        <div className="inline-flex items-center gap-2 text-muted-foreground text-sm">
          <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
          Loading audit results...
        </div>
      </div>
    );
  }

  if (error || !audit) {
    return (
      <div className="container mx-auto px-6 py-20 text-center space-y-3">
        <h2 className="text-xl font-bold">Audit Not Found</h2>
        <p className="text-sm text-muted-foreground">{error || "This audit does not exist."}</p>
      </div>
    );
  }

  const criticalCount = audit.gaps.filter((g) => g.severity === "critical").length;
  const highCount = audit.gaps.filter((g) => g.severity === "high").length;

  return (
    <div className="container mx-auto px-6 py-10 space-y-8 max-w-4xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{audit.document_name}</h1>
          <p className="text-sm text-muted-foreground mt-1">
            <Badge variant="outline" className="mr-2 text-xs">{audit.document_type}</Badge>
            {format(new Date(audit.timestamp), "MMM d, yyyy 'at' h:mm a")}
          </p>
        </div>
        <a
          href={getReportPdfUrl(audit.report_pdf_url)}
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button variant="outline" size="sm" className="border-border/50">
            Download PDF
          </Button>
        </a>
      </div>

      {/* Score Card */}
      <div className="gradient-border rounded-xl p-6 bg-card/40 space-y-4">
        <div className="flex items-end gap-4">
          <span className={`text-5xl font-bold font-mono ${scoreColor(audit.score)}`}>
            {audit.score}
          </span>
          <span className="text-muted-foreground text-lg mb-1">/ 100</span>
          <Badge variant="outline" className={`ml-2 text-base px-3 py-1 ${gradeStyle(audit.score)}`}>
            {audit.grade}
          </Badge>
        </div>
        <Progress
          value={audit.score}
          className={`h-2 bg-muted/30 ${progressColor(audit.score)}`}
        />
        <div className="flex gap-4 text-xs text-muted-foreground">
          {criticalCount > 0 && (
            <span className="text-red-400">{criticalCount} critical</span>
          )}
          {highCount > 0 && (
            <span className="text-orange-400">{highCount} high</span>
          )}
          <span>{audit.gaps.length} total gaps</span>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="space-y-2">
        <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Executive Summary</h2>
        <div className="rounded-xl border border-border/50 bg-card/30 p-5">
          <p className="text-sm leading-relaxed">{audit.executive_summary}</p>
        </div>
      </div>

      {/* Compliance Gaps */}
      <div className="space-y-3">
        <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Compliance Gaps</h2>
        <div className="space-y-3">
          {audit.gaps.map((gap, i) => (
            <div key={i} className="rounded-xl border border-border/50 bg-card/30 p-4 space-y-2">
              <div className="flex items-center gap-3">
                <Badge variant="outline" className={`${severityStyle[gap.severity]} text-xs capitalize`}>
                  {gap.severity}
                </Badge>
                <span className="font-medium text-sm">{gap.title}</span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">{gap.description}</p>
              <p className="text-xs text-muted-foreground/70 font-mono">{gap.regulation}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Remediation Steps */}
      <div className="space-y-2">
        <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Remediation Steps</h2>
        <div className="rounded-xl border border-border/50 bg-card/30 p-5 space-y-3">
          {audit.remediation.map((step, i) => (
            <div key={i} className="flex gap-3 text-sm">
              <span className="text-primary font-mono text-xs mt-0.5 shrink-0">{String(i + 1).padStart(2, "0")}</span>
              <p className="leading-relaxed">{step}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
