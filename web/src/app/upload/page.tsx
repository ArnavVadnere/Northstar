"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { runAudit } from "@/lib/api";

const REGULATIONS = ["SOX", "GDPR", "PCI-DSS", "HIPAA", "Basel III"] as const;

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [companyName, setCompanyName] = useState("");
  const [regulation, setRegulation] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

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
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !companyName || !regulation) return;

    setSubmitting(true);
    setError("");

    try {
      const { audit_id } = await runAudit(file, companyName, regulation);
      router.push(`/results/${audit_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Audit submission failed. Please try again.");
      setSubmitting(false);
    }
  };

  const isValid = file && companyName.trim() && regulation;

  return (
    <div className="container mx-auto px-6 py-10 max-w-2xl">
      <h1 className="text-3xl font-bold mb-2">Upload Document</h1>
      <p className="text-muted-foreground mb-8">
        Upload a financial document for AI-powered compliance analysis.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Picker */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Financial Document</CardTitle>
          </CardHeader>
          <CardContent>
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors cursor-pointer ${
                dragActive
                  ? "border-primary bg-primary/5"
                  : "border-muted-foreground/25 hover:border-muted-foreground/50"
              }`}
              onClick={() => document.getElementById("file-input")?.click()}
            >
              {file ? (
                <div className="space-y-1">
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <button
                    type="button"
                    className="text-sm text-destructive hover:underline mt-2"
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
                  <p className="text-muted-foreground">
                    Drag and drop your PDF here, or click to browse
                  </p>
                  <p className="text-xs text-muted-foreground">PDF up to 50MB</p>
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
          </CardContent>
        </Card>

        {/* Company Name */}
        <div className="space-y-2">
          <label htmlFor="company" className="text-sm font-medium">
            Company Name
          </label>
          <Input
            id="company"
            placeholder="e.g. Acme Financial Corp"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
          />
        </div>

        {/* Regulation Selector */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Regulation</label>
          <Select value={regulation} onValueChange={setRegulation}>
            <SelectTrigger>
              <SelectValue placeholder="Select a regulation to check against" />
            </SelectTrigger>
            <SelectContent>
              {REGULATIONS.map((reg) => (
                <SelectItem key={reg} value={reg}>
                  {reg}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {/* Submit */}
        <Button type="submit" className="w-full" size="lg" disabled={!isValid || submitting}>
          {submitting ? "Analyzing..." : "Run Compliance Audit"}
        </Button>
      </form>
    </div>
  );
}
