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

function ScoreBadge({ score }: { score: number }) {
  if (score >= 80) return <Badge className="bg-green-600">{score}</Badge>;
  if (score >= 60) return <Badge className="bg-yellow-600">{score}</Badge>;
  return <Badge variant="destructive">{score}</Badge>;
}

export default async function HistoryPage() {
  const audits = await getAuditHistory();
  return (
    <div className="container mx-auto px-6 py-10 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audit History</h1>
        <p className="text-muted-foreground mt-1">
          View all past compliance audits.
        </p>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Document</TableHead>
              <TableHead>Regulations</TableHead>
              <TableHead className="text-center">Score</TableHead>
              <TableHead className="text-center">Status</TableHead>
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
                    {audit.company_name}
                  </Link>
                </TableCell>
                <TableCell>
                  <Link href={`/results/${audit.audit_id}`} className="block text-sm">
                    {audit.document_name}
                  </Link>
                </TableCell>
                <TableCell>
                  <Link href={`/results/${audit.audit_id}`} className="flex gap-1">
                    {audit.regulations_checked.map((r) => (
                      <Badge key={r} variant="outline" className="text-xs">
                        {r}
                      </Badge>
                    ))}
                  </Link>
                </TableCell>
                <TableCell className="text-center">
                  <Link href={`/results/${audit.audit_id}`} className="block">
                    <ScoreBadge score={audit.compliance_score} />
                  </Link>
                </TableCell>
                <TableCell className="text-center">
                  <Link href={`/results/${audit.audit_id}`} className="block">
                    <Badge variant="secondary" className="capitalize">
                      {audit.status}
                    </Badge>
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
