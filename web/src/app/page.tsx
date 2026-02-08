import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getAuditHistory } from "@/lib/api";
import { format } from "date-fns";

function GradeBadge({ score, grade }: { score: number; grade: string }) {
  const color = score >= 80 ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" : score >= 60 ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" : "bg-red-500/20 text-red-400 border-red-500/30";
  return <Badge variant="outline" className={`${color} font-mono text-xs`}>{grade} {score}</Badge>;
}

export default async function Dashboard() {
  let audits: Awaited<ReturnType<typeof getAuditHistory>> = [];
  try {
    audits = await getAuditHistory();
  } catch {
    audits = [];
  }

  return (
    <div className="container mx-auto px-6 py-10 space-y-14">
      {/* Hero */}
      <section className="text-center space-y-5 py-20 relative">
        {/* Background gradient blobs */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-blue-600/8 rounded-full blur-[120px]" />
          <div className="absolute top-1/3 left-1/4 w-[300px] h-[300px] bg-purple-600/5 rounded-full blur-[100px]" />
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-gradient-to-r from-primary/10 to-purple-500/10 text-primary text-xs font-medium">
          <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
          AI-Powered Compliance
        </div>
        <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-br from-white via-foreground to-blue-200 bg-clip-text text-transparent">
          Financial Compliance
          <br />
          Auditor
        </h1>
        <p className="text-muted-foreground text-lg max-w-xl mx-auto leading-relaxed">
          Upload financial documents and get instant compliance analysis
          against SOX 404, 10-K, 8-K, and Invoice regulations.
        </p>
        <Link href="/upload">
          <Button size="lg" className="mt-2">
            Upload Document
          </Button>
        </Link>
      </section>

      {/* 3-Agent Feature Cards */}
      <section className="grid md:grid-cols-3 gap-5">
        {[
          {
            num: "01",
            title: "Compliance Researcher",
            desc: "Researches current compliance rules and regulations applicable to your document type using live web search.",
            gradient: "from-blue-500/20 via-transparent to-transparent",
            glow: "group-hover:shadow-blue-500/10",
          },
          {
            num: "02",
            title: "PDF Analyzer",
            desc: "Analyzes your document against compliance rules to identify gaps, missing sections, and non-compliance areas.",
            gradient: "from-cyan-500/20 via-transparent to-transparent",
            glow: "group-hover:shadow-cyan-500/10",
          },
          {
            num: "03",
            title: "Report Generator",
            desc: "Produces a scored report with executive summary, severity-rated gaps, and actionable remediation steps.",
            gradient: "from-purple-500/20 via-transparent to-transparent",
            glow: "group-hover:shadow-purple-500/10",
          },
        ].map((agent) => (
          <div
            key={agent.num}
            className={`group relative rounded-xl border border-border/50 bg-card/40 backdrop-blur-sm p-5 transition-all duration-300 hover:border-primary/40 hover:bg-card/60 hover:shadow-xl hover:-translate-y-1 ${agent.glow} cursor-default`}
          >
            {/* Top gradient highlight */}
            <div className={`absolute inset-0 rounded-xl bg-gradient-to-br ${agent.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none`} />

            <div className="relative space-y-3">
              <div className="text-[11px] font-mono tracking-widest text-primary/70 group-hover:text-primary transition-colors">
                AGENT {agent.num}
              </div>
              <h3 className="font-semibold text-sm group-hover:text-white transition-colors">{agent.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{agent.desc}</p>
            </div>
          </div>
        ))}
      </section>

      {/* Recent Audits */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">Recent Audits</h2>
        {audits.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border/50 p-10 text-center">
            <p className="text-muted-foreground text-sm">No audits yet. Upload a document to get started.</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {audits.slice(0, 5).map((audit) => (
              <Link key={audit.audit_id} href={`/results/${audit.audit_id}`}>
                <div className="flex items-center justify-between gap-4 p-4 rounded-xl border border-border/50 bg-card/30 hover:bg-card/60 hover:border-primary/30 transition-all duration-200 cursor-pointer group">
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-primary/20 to-blue-400/10 flex items-center justify-center shrink-0 group-hover:from-primary/30 group-hover:to-blue-400/20 transition-all">
                      <span className="text-primary text-xs font-mono">{audit.document_type.slice(0, 3).toUpperCase()}</span>
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-sm truncate group-hover:text-primary transition-colors">{audit.document_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {format(new Date(audit.timestamp), "MMM d, yyyy")}
                      </p>
                    </div>
                  </div>
                  <GradeBadge score={audit.score} grade={audit.grade} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
