import { notFound } from "next/navigation";
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
import { getAuditResult } from "@/lib/api";
import { format } from "date-fns";
import type { Finding } from "@/lib/types";

const severityColor: Record<Finding["severity"], string> = {
  critical: "bg-red-600",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-blue-500",
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

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ audit_id: string }>;
}) {
  const { audit_id } = await params;

  let audit;
  try {
    audit = await getAuditResult(audit_id);
  } catch {
    return notFound();
  }

  const criticalCount = audit.findings.filter((f) => f.severity === "critical").length;
  const highCount = audit.findings.filter((f) => f.severity === "high").length;

  return (
    <div className="container mx-auto px-6 py-10 space-y-8 max-w-4xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">{audit.company_name}</h1>
          <p className="text-muted-foreground mt-1">
            {audit.document_name} &middot;{" "}
            {format(new Date(audit.timestamp), "MMM d, yyyy 'at' h:mm a")}
          </p>
          <div className="flex gap-2 mt-2">
            {audit.regulations_checked.map((r) => (
              <Badge key={r} variant="outline">
                {r}
              </Badge>
            ))}
          </div>
        </div>
        <Button variant="outline" disabled>
          Export PDF
        </Button>
      </div>

      <Separator />

      {/* Score */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Compliance Score</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-end gap-3">
            <span className={`text-5xl font-bold ${scoreColor(audit.compliance_score)}`}>
              {audit.compliance_score}
            </span>
            <span className="text-muted-foreground text-lg mb-1">/ 100</span>
          </div>
          <Progress
            value={audit.compliance_score}
            className={`h-3 ${progressColor(audit.compliance_score)}`}
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
            <span>{audit.findings.length} total findings</span>
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

      {/* Findings Table */}
      <div className="space-y-3">
        <h2 className="text-xl font-semibold">Findings</h2>
        <div className="rounded-md border overflow-x-auto">
          <Table className="min-w-[640px]">
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">Severity</TableHead>
                <TableHead className="w-[160px]">Regulation</TableHead>
                <TableHead>Issue</TableHead>
                <TableHead>Remediation</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {audit.findings.map((finding) => (
                <TableRow key={finding.id}>
                  <TableCell>
                    <Badge className={`${severityColor[finding.severity]} text-white capitalize`}>
                      {finding.severity}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-medium text-sm">
                    {finding.regulation}
                  </TableCell>
                  <TableCell className="text-sm">{finding.issue}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {finding.remediation}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
