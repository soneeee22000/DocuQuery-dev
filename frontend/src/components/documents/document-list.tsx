"use client";

/**
 * Document list component.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import type { Document } from "@/types/document";

import { DeleteDialog } from "./delete-dialog";

interface DocumentListProps {
  documents: Document[];
  isLoading: boolean;
  onDelete: (documentId: string) => Promise<void>;
}

/** Format file size in human-readable form. */
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** Format doc_type to a readable badge label. */
function docTypeBadge(docType: string): string {
  return docType === "resume" ? "Resume" : "Job Description";
}

export function DocumentList({
  documents,
  isLoading,
  onDelete,
}: DocumentListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return <EmptyState message="Upload a document to get started." />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Documents</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="divide-y">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between py-3"
            >
              <div className="space-y-1">
                <p className="text-sm font-medium">{doc.name}</p>
                <div className="flex gap-2 text-xs text-muted-foreground">
                  <span className="rounded bg-muted px-1.5 py-0.5">
                    {docTypeBadge(doc.doc_type)}
                  </span>
                  <span>{formatFileSize(doc.file_size)}</span>
                  <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <DeleteDialog
                documentName={doc.name}
                onConfirm={() => onDelete(doc.id)}
              />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
