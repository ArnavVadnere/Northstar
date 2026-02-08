import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getAuditHistory } from "@/lib/api";
import { format } from "date-fns";

function GradeBadge({ score, grade }: { score: number; grade: string }) {
  const color = score >= 80 ? "bg-green-600" : score >= 60 ? "bg-yellow-600" : "bg-red-600";
  return <Badge className={color}>{grade} ({score})</Badge>;
}

export default async function Dashboard() {
  let audits;
  try {
    audits = await getAuditHistory();
  } catch {
    audits = [];
  }

  return (
    <div className="container mx-auto px-6 py-10 space-y-10">
      {/* Hero */}
      <section className="text-center space-y-4 py-12">
        <h1 className="text-4xl font-bold tracking-tight">
          Financial Compliance Auditor
        </h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          Upload financial documents and get instant AI-powered compliance analysis
          against SOX 404, 10-K, 8-K, and Invoice regulations.
        </p>
        <Link href="/upload">
          <Button size="lg" className="mt-4">
            Upload Financial Document
          </Button>
        </Link>
      </section>

      {/* 3-Agent Feature Cards */}
      <section className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Agent 1: Compliance Researcher</CardTitle>
            <CardDescription>
              Researches current compliance rules and regulations applicable to your
              document type using live web search.
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Agent 2: PDF Analyzer</CardTitle>
            <CardDescription>
              Analyzes your document against compliance rules to identify gaps,
              missing sections, and areas of non-compliance.
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Agent 3: Report Generator</CardTitle>
            <CardDescription>
              Produces a compliance report with score, grade, executive summary,
              severity-rated gaps, and remediation steps.
            </CardDescription>
          </CardHeader>
        </Card>
      </section>

      {/* Recent Audits */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Recent Audits</h2>
        {audits.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-muted-foreground">No audits yet. Upload a document to get started.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {audits.map((audit) => (
              <Link key={audit.audit_id} href={`/results/${audit.audit_id}`}>
                <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
                  <CardContent className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4">
                    <div className="space-y-1">
                      <p className="font-medium">{audit.document_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {audit.document_type} &middot;{" "}
                        {format(new Date(audit.timestamp), "MMM d, yyyy")}
                      </p>
                    </div>
                    <GradeBadge score={audit.score} grade={audit.grade} />
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
