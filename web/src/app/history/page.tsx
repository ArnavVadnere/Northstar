import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { getAuditHistory } from "@/lib/api";
import { format } from "date-fns";

function GradeBadge({ score, grade }: { score: number; grade: string }) {
  const color = score >= 80 ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : score >= 60 ? "bg-yellow-500/15 text-yellow-400 border-yellow-500/30" : "bg-red-500/15 text-red-400 border-red-500/30";
  return <Badge variant="outline" className={`${color} font-mono text-xs`}>{grade} {score}</Badge>;
}

export default async function HistoryPage() {
  let audits: Awaited<ReturnType<typeof getAuditHistory>> = [];
  try {
    audits = await getAuditHistory();
  } catch {
    audits = [];
  }

  return (
    <div className="container mx-auto px-6 py-10 space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">Audit History</h1>
        <p className="text-sm text-muted-foreground mt-1">
          All past compliance audits.
        </p>
      </div>

      {audits.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border/50 p-10 text-center">
          <p className="text-sm text-muted-foreground">No audits found. Upload a document to get started.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {audits.map((audit) => (
            <Link key={audit.audit_id} href={`/results/${audit.audit_id}`}>
              <div className="flex items-center justify-between gap-4 p-4 rounded-xl border border-border/50 bg-card/30 hover:bg-card/60 transition-colors cursor-pointer group">
                <div className="flex items-center gap-4 min-w-0">
                  <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                    <span className="text-primary text-[10px] font-mono">{audit.document_type.slice(0, 3).toUpperCase()}</span>
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium text-sm truncate group-hover:text-primary transition-colors">{audit.document_name}</p>
                    <p className="text-xs text-muted-foreground">
                      {format(new Date(audit.timestamp), "MMM d, yyyy 'at' h:mm a")}
                    </p>
                  </div>
                </div>
                <GradeBadge score={audit.score} grade={audit.grade} />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
