"use client";

/**
 * Drag-and-drop file upload component.
 */

import { useCallback, useRef, useState } from "react";
import { AxiosError } from "axios";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import type { ApiResponse } from "@/types/api";
import type { DocType, Document } from "@/types/document";

const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;
const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"];

interface FileUploadProps {
  onUpload: (file: File, docType: DocType) => Promise<Document>;
}

export function FileUpload({ onUpload }: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [docType, setDocType] = useState<DocType>("resume");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    if (file.size > MAX_SIZE_BYTES) {
      return `File exceeds ${MAX_SIZE_MB}MB limit`;
    }
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `Unsupported format. Allowed: ${ALLOWED_EXTENSIONS.join(", ")}`;
    }
    return null;
  };

  const handleFile = useCallback(
    async (file: File) => {
      const validationError = validateFile(file);
      if (validationError) {
        toast.error(validationError);
        return;
      }

      setIsUploading(true);
      try {
        await onUpload(file, docType);
        toast.success(`Uploaded ${file.name} successfully`);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      } catch (err) {
        if (err instanceof AxiosError && err.response?.data) {
          const body = err.response.data as ApiResponse<unknown>;
          toast.error(body.error?.message ?? "Upload failed");
        } else {
          toast.error("Upload failed");
        }
      } finally {
        setIsUploading(false);
      }
    },
    [docType, onUpload],
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Document</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Document Type</Label>
          <div className="flex gap-2">
            <Button
              type="button"
              variant={docType === "resume" ? "default" : "outline"}
              size="sm"
              onClick={() => setDocType("resume")}
            >
              Resume
            </Button>
            <Button
              type="button"
              variant={docType === "job_description" ? "default" : "outline"}
              size="sm"
              onClick={() => setDocType("job_description")}
            >
              Job Description
            </Button>
          </div>
        </div>

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors ${
            isDragOver
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25 hover:border-primary/50"
          }`}
        >
          <p className="text-sm font-medium">
            {isUploading
              ? "Uploading..."
              : "Drag & drop a file here, or click to browse"}
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            PDF, DOCX, or TXT (max {MAX_SIZE_MB}MB)
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleInputChange}
            className="hidden"
          />
        </div>
      </CardContent>
    </Card>
  );
}
