import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getAuditHistory } from "@/lib/api";
import { format } from "date-fns";

function ScoreBadge({ score }: { score: number }) {
  if (score >= 80) return <Badge className="bg-green-600">{score}</Badge>;
  if (score >= 60) return <Badge className="bg-yellow-600">{score}</Badge>;
  return <Badge variant="destructive">{score}</Badge>;
}

export default async function Dashboard() {
  const audits = await getAuditHistory();
  return (
    <div className="container mx-auto px-6 py-10 space-y-10">
      {/* Hero */}
      <section className="text-center space-y-4 py-12">
        <h1 className="text-4xl font-bold tracking-tight">
          Financial Compliance Auditor
        </h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          Upload financial documents and get instant AI-powered compliance analysis
          against SOX, GDPR, PCI-DSS, HIPAA, and Basel III regulations.
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
            <CardTitle className="text-base">Agent 1: Regulation Identifier</CardTitle>
            <CardDescription>
              Automatically identifies which regulations apply to your document based on
              industry, jurisdiction, and content type.
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Agent 2: Gap Analyzer</CardTitle>
            <CardDescription>
              Scans your document against applicable regulations to find compliance gaps,
              missing sections, and areas of concern.
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Agent 3: Report Generator</CardTitle>
            <CardDescription>
              Produces a comprehensive compliance report with a score, executive summary,
              severity-rated findings, and remediation steps.
            </CardDescription>
          </CardHeader>
        </Card>
      </section>

      {/* Recent Audits */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Recent Audits</h2>
        <div className="grid gap-4">
          {audits.map((audit) => (
            <Link key={audit.audit_id} href={`/results/${audit.audit_id}`}>
              <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
                <CardContent className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4">
                  <div className="space-y-1">
                    <p className="font-medium">{audit.company_name}</p>
                    <p className="text-sm text-muted-foreground">
                      {audit.document_name} &middot;{" "}
                      {format(new Date(audit.timestamp), "MMM d, yyyy")}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      {audit.regulations_checked.map((r) => (
                        <Badge key={r} variant="outline" className="text-xs">
                          {r}
                        </Badge>
                      ))}
                    </div>
                    <ScoreBadge score={audit.compliance_score} />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
