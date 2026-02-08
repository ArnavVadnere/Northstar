import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getAuditHistory } from "@/lib/api";
import { format } from "date-fns";

function GradeBadge({ score, grade }: { score: number; grade: string }) {
  const color = score >= 80 ? "bg-green-600" : score >= 60 ? "bg-yellow-600" : "bg-red-600";
  return <Badge className={color}>{grade} ({score})</Badge>;
}

export default async function HistoryPage() {
  let audits: Awaited<ReturnType<typeof getAuditHistory>> = [];
  try {
    audits = await getAuditHistory();
  } catch {
    audits = [];
  }

  return (
    <div className="container mx-auto px-6 py-10 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audit History</h1>
        <p className="text-muted-foreground mt-1">
          View all past compliance audits.
        </p>
      </div>

      {audits.length === 0 ? (
        <div className="rounded-md border p-10 text-center">
          <p className="text-muted-foreground">No audits found. Upload a document to get started.</p>
        </div>
      ) : (
        <div className="rounded-md border overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Document</TableHead>
                <TableHead>Type</TableHead>
                <TableHead className="text-center">Score</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {audits.map((audit) => (
                <TableRow key={audit.audit_id} className="cursor-pointer hover:bg-muted/50">
                  <TableCell>
                    <Link href={`/results/${audit.audit_id}`} className="block">
                      {format(new Date(audit.timestamp), "MMM d, yyyy")}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Link href={`/results/${audit.audit_id}`} className="block font-medium">
                      {audit.document_name}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Link href={`/results/${audit.audit_id}`} className="block">
                      <Badge variant="outline">{audit.document_type}</Badge>
                    </Link>
                  </TableCell>
                  <TableCell className="text-center">
                    <Link href={`/results/${audit.audit_id}`} className="block">
                      <GradeBadge score={audit.score} grade={audit.grade} />
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
