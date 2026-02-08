"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getAuditResult, getReportPdfUrl } from "@/lib/api";
import { getCachedAudit } from "@/lib/audit-cache";
import { format } from "date-fns";
import type { AuditResult, ComplianceGap } from "@/lib/types";

const severityColor: Record<ComplianceGap["severity"], string> = {
  critical: "bg-red-600",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
};

function scoreColor(score: number) {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-yellow-600";
  return "text-red-600";
}

function progressColor(score: number) {
  if (score >= 80) return "[&>div]:bg-green-600";
  if (score >= 60) return "[&>div]:bg-yellow-500";
  return "[&>div]:bg-red-600";
}

function gradeColor(score: number) {
  if (score >= 80) return "bg-green-600";
  if (score >= 60) return "bg-yellow-600";
  return "bg-red-600";
}

export default function ResultsPage() {
  const params = useParams();
  const auditId = params.audit_id as string;

  const [audit, setAudit] = useState<AuditResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      // Check client-side cache first (from POST /api/run-audit response)
      const cached = getCachedAudit(auditId);
      if (cached) {
        setAudit(cached);
        setLoading(false);
        return;
      }

      // Fall back to GET /api/audit/{id}
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
        <p className="text-muted-foreground">Loading audit results...</p>
      </div>
    );
  }

  if (error || !audit) {
    return (
      <div className="container mx-auto px-6 py-20 text-center space-y-4">
        <h2 className="text-2xl font-bold">Audit Not Found</h2>
        <p className="text-muted-foreground">{error || "This audit does not exist."}</p>
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
          <h1 className="text-3xl font-bold">{audit.document_name}</h1>
          <p className="text-muted-foreground mt-1">
            {audit.document_type} &middot;{" "}
            {format(new Date(audit.timestamp), "MMM d, yyyy 'at' h:mm a")}
          </p>
        </div>
        <a
          href={getReportPdfUrl(audit.report_pdf_url)}
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button variant="outline">Download PDF Report</Button>
        </a>
      </div>

      <Separator />

      {/* Score */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Compliance Score</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-end gap-3">
            <span className={`text-5xl font-bold ${scoreColor(audit.score)}`}>
              {audit.score}
            </span>
            <span className="text-muted-foreground text-lg mb-1">/ 100</span>
            <Badge className={`ml-2 text-lg px-3 py-1 ${gradeColor(audit.score)} text-white`}>
              {audit.grade}
            </Badge>
          </div>
          <Progress
            value={audit.score}
            className={`h-3 ${progressColor(audit.score)}`}
          />
          <div className="flex gap-4 text-sm text-muted-foreground">
            {criticalCount > 0 && (
              <span className="text-red-600 font-medium">
                {criticalCount} critical
              </span>
            )}
            {highCount > 0 && (
              <span className="text-orange-500 font-medium">
                {highCount} high
              </span>
            )}
            <span>{audit.gaps.length} total gaps</span>
          </div>
        </CardContent>
      </Card>

      {/* Executive Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Executive Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-relaxed">{audit.executive_summary}</p>
        </CardContent>
      </Card>

      {/* Compliance Gaps Table */}
      <div className="space-y-3">
        <h2 className="text-xl font-semibold">Compliance Gaps</h2>
        <div className="rounded-md border overflow-x-auto">
          <Table className="min-w-[640px]">
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">Severity</TableHead>
                <TableHead className="w-[200px]">Gap</TableHead>
                <TableHead>Description</TableHead>
                <TableHead className="w-[200px]">Regulation</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {audit.gaps.map((gap, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <Badge className={`${severityColor[gap.severity]} text-white capitalize`}>
                      {gap.severity}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-medium text-sm">
                    {gap.title}
                  </TableCell>
                  <TableCell className="text-sm">
                    {gap.description}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {gap.regulation}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Remediation Steps */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Remediation Steps</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-2 text-sm">
            {audit.remediation.map((step, i) => (
              <li key={i} className="leading-relaxed">{step}</li>
            ))}
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
