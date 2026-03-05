"use client";

/**
 * Documents page with upload and list.
 */

import { useEffect } from "react";
import { toast } from "sonner";

import { DocumentList } from "@/components/documents/document-list";
import { FileUpload } from "@/components/documents/file-upload";
import { useDocuments } from "@/hooks/use-documents";

export default function DocumentsPage() {
  const { documents, isLoading, error, upload, remove } = useDocuments();

  useEffect(() => {
    if (error) toast.error(error);
  }, [error]);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h2 className="text-2xl font-semibold">Documents</h2>
      <FileUpload onUpload={upload} />
      <DocumentList
        documents={documents}
        isLoading={isLoading}
        onDelete={remove}
      />
    </div>
  );
}
