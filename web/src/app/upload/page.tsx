"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { runAudit } from "@/lib/api";
import { cacheAudit } from "@/lib/audit-cache";

const DOCUMENT_TYPES = ["SOX 404", "10-K", "8-K", "Invoice"] as const;

const PIPELINE_STEPS = [
  { label: "Extracting PDF content", duration: 3000 },
  { label: "Validating document type", duration: 4000 },
  { label: "Researching compliance rules", duration: 12000 },
  { label: "Analyzing document against regulations", duration: 25000 },
  { label: "Identifying compliance gaps", duration: 15000 },
  { label: "Generating compliance report", duration: 15000 },
  { label: "Building PDF report", duration: 5000 },
];

function TerminalLoading({ stepIndex }: { stepIndex: number }) {
  return (
    <div className="rounded-xl border border-border/50 bg-[hsl(222,47%,8%)] p-5 font-mono text-xs space-y-1.5 max-w-lg mx-auto">
      <div className="flex items-center gap-2 mb-3">
        <span className="h-2.5 w-2.5 rounded-full bg-red-500/80" />
        <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/80" />
        <span className="h-2.5 w-2.5 rounded-full bg-green-500/80" />
        <span className="text-muted-foreground ml-2 text-[10px]">northstar-audit</span>
      </div>
      {PIPELINE_STEPS.map((step, i) => {
        if (i > stepIndex) return null;
        const isDone = i < stepIndex;
        const isCurrent = i === stepIndex;
        return (
          <div key={i} className="flex items-center gap-2">
            <span className={isDone ? "text-emerald-400" : isCurrent ? "text-primary" : "text-muted-foreground"}>
              {isDone ? "[done]" : isCurrent ? "[....]" : "[    ]"}
            </span>
            <span className={isDone ? "text-muted-foreground" : isCurrent ? "text-foreground" : "text-muted-foreground"}>
              {step.label}
              {isDone && <span className="text-muted-foreground/50 ml-2">ok</span>}
              {isCurrent && <span className="terminal-cursor text-primary ml-0.5">_</span>}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [stepIndex, setStepIndex] = useState(0);

  // Advance through terminal steps while submitting
  useEffect(() => {
    if (!submitting) {
      setStepIndex(0);
      return;
    }
    if (stepIndex >= PIPELINE_STEPS.length - 1) return;

    const timer = setTimeout(() => {
      setStepIndex((prev) => Math.min(prev + 1, PIPELINE_STEPS.length - 1));
    }, PIPELINE_STEPS[stepIndex].duration);

    return () => clearTimeout(timer);
  }, [submitting, stepIndex]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0]);
      setError("");
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setError("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !documentType) return;

    setSubmitting(true);
    setError("");
    setStepIndex(0);

    try {
      const result = await runAudit(file, documentType, "web-user");
      cacheAudit(result);
      router.push(`/results/${result.audit_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Audit submission failed. Please try again.");
      setSubmitting(false);
    }
  };

  const isValid = file && documentType;

  if (submitting) {
    return (
      <div className="container mx-auto px-6 py-16 max-w-2xl space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold">Running Compliance Audit</h1>
          <p className="text-sm text-muted-foreground">
            Processing <span className="text-foreground font-medium">{file?.name}</span>
          </p>
        </div>
        <TerminalLoading stepIndex={stepIndex} />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-10 max-w-lg">
      <h1 className="text-2xl font-bold mb-1">Upload Document</h1>
      <p className="text-sm text-muted-foreground mb-8">
        Upload a financial document for AI-powered compliance analysis.
      </p>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* File Picker */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`rounded-xl border-2 border-dashed p-8 text-center transition-all cursor-pointer ${
            dragActive
              ? "border-primary bg-primary/5"
              : file
              ? "border-primary/30 bg-card/30"
              : "border-border/50 hover:border-border bg-card/20"
          }`}
          onClick={() => document.getElementById("file-input")?.click()}
        >
          {file ? (
            <div className="space-y-1">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-primary/10 text-primary text-xs font-mono">
                {file.name}
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
              <button
                type="button"
                className="text-xs text-red-400 hover:text-red-300 mt-2"
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
              >
                Remove
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="h-10 w-10 mx-auto rounded-lg bg-muted/50 flex items-center justify-center">
                <svg className="h-5 w-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
              </div>
              <p className="text-sm text-muted-foreground">
                Drop your PDF here, or click to browse
              </p>
              <p className="text-[11px] text-muted-foreground/60">PDF up to 50MB</p>
            </div>
          )}
          <input
            id="file-input"
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>

        {/* Document Type Selector */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Document Type</label>
          <Select value={documentType} onValueChange={setDocumentType}>
            <SelectTrigger className="bg-card/30 border-border/50">
              <SelectValue placeholder="Select document type" />
            </SelectTrigger>
            <SelectContent>
              {DOCUMENT_TYPES.map((type) => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Submit */}
        <Button type="submit" className="w-full glow-blue" size="lg" disabled={!isValid}>
          Run Compliance Audit
        </Button>
      </form>
    </div>
  );
}
