"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface FileEntry {
  filename: string;
  size: number;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function UploadPage() {
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const fetchFiles = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/files`);
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const data = await res.json();
      setFiles(data.files ?? []);
    } catch (e) {
      console.error("Failed to load files:", e);
      setError("Failed to load files.");
    }
  }, []);

  const uploadFiles = useCallback(
    async (selected: FileList | File[]) => {
      if (!selected || selected.length === 0) return;
      setUploading(true);
      setError(null);
      setSuccess(null);

      const form = new FormData();
      Array.from(selected).forEach((f) => form.append("files", f));

      try {
        const res = await fetch(`${API_BASE}/upload`, {
          method: "POST",
          body: form,
        });
        if (!res.ok) throw new Error(`Upload failed (${res.status})`);
        const data = await res.json();
        setSuccess(
          `Uploaded ${data.uploaded.length} file(s) successfully.`
        );
        await fetchFiles();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed.");
      } finally {
        setUploading(false);
      }
    },
    [fetchFiles]
  );

  const deleteFile = useCallback(
    async (filename: string) => {
      setError(null);
      try {
        const res = await fetch(
          `${API_BASE}/files/${encodeURIComponent(filename)}`,
          { method: "DELETE" }
        );
        if (!res.ok) throw new Error(`Delete failed (${res.status})`);
        await fetchFiles();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Delete failed.");
      }
    },
    [fetchFiles]
  );

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragging(false);
      uploadFiles(e.dataTransfer.files);
    },
    [uploadFiles]
  );

  // Load files on first render
  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col items-center py-16 px-4">
      <h1 className="text-3xl font-bold mb-2 text-blue-400">File Upload</h1>
      <p className="text-gray-400 mb-8">Upload, browse, and manage your files.</p>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`w-full max-w-xl border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors
          ${dragging ? "border-blue-400 bg-blue-950" : "border-gray-600 hover:border-blue-500 hover:bg-gray-900"}`}
      >
        <p className="text-gray-300 text-lg">
          {dragging ? "Drop files here…" : "Drag & drop files here, or click to select"}
        </p>
        <p className="text-gray-500 text-sm mt-1">Any file type accepted</p>
        <input
          ref={inputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => e.target.files && uploadFiles(e.target.files)}
        />
      </div>

      {/* Status messages */}
      {uploading && (
        <p className="mt-4 text-blue-400 animate-pulse">Uploading…</p>
      )}
      {success && (
        <p className="mt-4 text-green-400">{success}</p>
      )}
      {error && (
        <p className="mt-4 text-red-400">{error}</p>
      )}

      {/* File list */}
      <div className="w-full max-w-xl mt-10">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-semibold text-gray-200">Uploaded Files</h2>
          <button
            onClick={fetchFiles}
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            Refresh
          </button>
        </div>

        {files.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No files uploaded yet.</p>
        ) : (
          <ul className="space-y-2">
            {files.map((file) => (
              <li
                key={file.filename}
                className="flex items-center justify-between bg-gray-800 rounded-lg px-4 py-3"
              >
                <div className="overflow-hidden">
                  <a
                    href={`${API_BASE}/files/${encodeURIComponent(file.filename)}`}
                    download={file.filename}
                    className="text-blue-300 hover:text-blue-200 truncate block"
                  >
                    {file.filename}
                  </a>
                  <span className="text-gray-500 text-xs">{formatBytes(file.size)}</span>
                </div>
                <button
                  onClick={() => deleteFile(file.filename)}
                  className="ml-4 text-red-400 hover:text-red-300 text-sm flex-shrink-0 transition-colors"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

