function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-muted ${className ?? ""}`} />;
}

export default function HistoryLoading() {
  return (
    <div className="container mx-auto px-6 py-10 space-y-6">
      <div>
        <Skeleton className="h-9 w-48" />
        <Skeleton className="h-5 w-64 mt-2" />
      </div>
      <div className="rounded-md border">
        <div className="p-4 space-y-4">
          {/* Header row */}
          <div className="grid grid-cols-6 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="h-4" />
            ))}
          </div>
          {/* Data rows */}
          {[1, 2, 3, 4].map((row) => (
            <div key={row} className="grid grid-cols-6 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Skeleton key={i} className="h-5" />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
