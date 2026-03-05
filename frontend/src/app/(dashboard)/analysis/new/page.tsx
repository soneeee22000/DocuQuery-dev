"use client";

/**
 * New analysis page — select resume + JD, trigger analysis.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useAnalysisTrigger } from "@/hooks/use-analysis";
import { listDocuments } from "@/lib/documents";
import type { Document } from "@/types/document";

export default function NewAnalysisPage() {
  const router = useRouter();
  const { trigger, isLoading } = useAnalysisTrigger();

  const [resumes, setResumes] = useState<Document[]>([]);
  const [jds, setJds] = useState<Document[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [jdId, setJdId] = useState("");
  const [docsLoading, setDocsLoading] = useState(true);

  useEffect(() => {
    Promise.all([listDocuments("resume"), listDocuments("job_description")])
      .then(([r, j]) => {
        setResumes(r);
        setJds(j);
      })
      .catch(() => {
        toast.error("Failed to load documents");
      })
      .finally(() => {
        setDocsLoading(false);
      });
  }, []);

  const handleAnalyze = async () => {
    if (!resumeId || !jdId) return;
    const result = await trigger({ resume_id: resumeId, jd_id: jdId });
    if (result) {
      router.push(`/analysis/${result.id}`);
    }
  };

  if (docsLoading) {
    return (
      <div className="mx-auto max-w-lg space-y-6">
        <h2 className="text-2xl font-semibold">New Analysis</h2>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (resumes.length === 0 || jds.length === 0) {
    return (
      <div className="mx-auto max-w-lg space-y-6">
        <h2 className="text-2xl font-semibold">New Analysis</h2>
        <EmptyState
          message={
            resumes.length === 0 && jds.length === 0
              ? "Upload a resume and a job description to start analyzing."
              : resumes.length === 0
                ? "Upload a resume to start analyzing."
                : "Upload a job description to start analyzing."
          }
          action={
            <Button asChild>
              <Link href="/documents">Upload Documents</Link>
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h2 className="text-2xl font-semibold">New Analysis</h2>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Select documents to analyze
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Resume</label>
            <Select value={resumeId} onValueChange={setResumeId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a resume" />
              </SelectTrigger>
              <SelectContent>
                {resumes.map((doc) => (
                  <SelectItem key={doc.id} value={doc.id}>
                    {doc.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Job Description</label>
            <Select value={jdId} onValueChange={setJdId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a job description" />
              </SelectTrigger>
              <SelectContent>
                {jds.map((doc) => (
                  <SelectItem key={doc.id} value={doc.id}>
                    {doc.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button
            onClick={handleAnalyze}
            disabled={!resumeId || !jdId || isLoading}
            className="w-full"
          >
            {isLoading ? "Analyzing..." : "Analyze Match"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
