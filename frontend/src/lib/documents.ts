/**
 * Document API functions.
 */

import type { ApiResponse } from "@/types/api";
import type { DocType, Document } from "@/types/document";

import apiClient from "./api-client";

/** Upload a document file. */
export async function uploadDocument(
  file: File,
  docType: DocType,
): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("doc_type", docType);

  const { data } = await apiClient.post<ApiResponse<Document>>(
    "/documents/upload",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return data.data!;
}

/** List documents, optionally filtered by type. */
export async function listDocuments(docType?: DocType): Promise<Document[]> {
  const params = docType ? { doc_type: docType } : {};
  const { data } = await apiClient.get<ApiResponse<Document[]>>("/documents/", {
    params,
  });
  return data.data!;
}

/** Delete a document by ID. */
export async function deleteDocument(documentId: string): Promise<void> {
  await apiClient.delete(`/documents/${documentId}`);
}
