"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, ApiError, type Resume } from "@/lib/api";
import { Empty, ErrorBox, Loading } from "@/components/States";
import StatusBadge from "@/components/StatusBadge";

const MAX_MB = 5;

export default function ResumePage() {
  const router = useRouter();
  const [resumes, setResumes] = useState<Resume[] | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listResumes()
      .then(setResumes)
      .catch((e: Error) => setError(e.message));
  }, []);

  async function onUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;

    const ext = file.name.toLowerCase().split(".").pop();
    if (ext !== "pdf" && ext !== "docx") {
      setError("Only PDF and DOCX files are accepted.");
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`The maximum file size is ${MAX_MB} MB.`);
      return;
    }

    setUploading(true);
    setError(null);
    try {
      const resume = await api.uploadResume(file);
      router.push(`/resume/${resume.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed.");
      setUploading(false);
    }
  }

  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold">Resume</h1>

      <form onSubmit={onUpload} className="mb-8 rounded border bg-white p-4">
        <label htmlFor="resume-file" className="mb-2 block text-sm font-medium">
          Upload a resume (PDF or DOCX, up to {MAX_MB} MB)
        </label>
        <input
          id="resume-file"
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="mb-3 block w-full text-sm"
        />
        <button
          type="submit"
          disabled={!file || uploading}
          className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </form>

      {error && <ErrorBox message={error} />}

      <h2 className="mb-2 mt-6 text-lg font-semibold">Your resumes</h2>
      {resumes === null && !error && <Loading />}
      {resumes?.length === 0 && <Empty message="No resumes yet. Upload one above." />}
      <ul className="space-y-2">
        {resumes?.map((r) => (
          <li key={r.id} className="flex items-center justify-between rounded border bg-white p-3">
            <div>
              <Link href={`/resume/${r.id}`} className="font-medium underline">
                {r.original_filename}
              </Link>
              <div className="text-sm text-gray-500">
                {new Date(r.created_at).toLocaleDateString()}
              </div>
            </div>
            <StatusBadge status={r.status} />
          </li>
        ))}
      </ul>
    </div>
  );
}