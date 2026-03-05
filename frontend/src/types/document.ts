/** Document type enum. */
export type DocType = "resume" | "job_description";

/** Document object returned from the API. */
export interface Document {
  id: string;
  name: string;
  doc_type: DocType;
  mime_type: string;
  file_size: number;
  extracted_text: string | null;
  created_at: string;
  updated_at: string;
}
