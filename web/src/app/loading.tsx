import { Card, CardContent, CardHeader } from "@/components/ui/card";

function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-muted ${className ?? ""}`} />;
}

export default function DashboardLoading() {
  return (
    <div className="container mx-auto px-6 py-10 space-y-10">
      {/* Hero skeleton */}
      <section className="text-center space-y-4 py-12">
        <Skeleton className="h-10 w-96 mx-auto" />
        <Skeleton className="h-5 w-[28rem] mx-auto" />
        <Skeleton className="h-11 w-52 mx-auto mt-4" />
      </section>

      {/* Feature cards skeleton */}
      <section className="grid md:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader className="space-y-2">
              <Skeleton className="h-5 w-48" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardHeader>
          </Card>
        ))}
      </section>

      {/* Recent audits skeleton */}
      <section className="space-y-4">
        <Skeleton className="h-7 w-40" />
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="flex items-center justify-between p-4">
              <div className="space-y-2">
                <Skeleton className="h-5 w-48" />
                <Skeleton className="h-4 w-64" />
              </div>
              <Skeleton className="h-6 w-12" />
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}
