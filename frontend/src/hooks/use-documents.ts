"use client";

/**
 * Hook for document CRUD operations.
 */

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

import { deleteDocument, listDocuments, uploadDocument } from "@/lib/documents";
import type { DocType, Document } from "@/types/document";

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } catch {
      setError("Failed to load documents");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const upload = useCallback(async (file: File, docType: DocType) => {
    const doc = await uploadDocument(file, docType);
    setDocuments((prev) => [doc, ...prev]);
    return doc;
  }, []);

  const remove = useCallback(async (documentId: string) => {
    try {
      await deleteDocument(documentId);
      setDocuments((prev) => prev.filter((d) => d.id !== documentId));
    } catch {
      toast.error("Failed to delete document");
    }
  }, []);

  return {
    documents,
    isLoading,
    error,
    upload,
    remove,
    refresh: fetchDocuments,
  };
}
