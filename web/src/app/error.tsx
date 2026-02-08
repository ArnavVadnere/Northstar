"use client";

import { Button } from "@/components/ui/button";

export default function Error({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="container mx-auto px-6 py-20 text-center space-y-4">
      <h2 className="text-2xl font-bold">Something went wrong</h2>
      <p className="text-muted-foreground">
        Failed to load data. The backend may be unavailable.
      </p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
