
"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  api,
  ApiError,
  type Analysis,
  type Education,
  type Experience,
  type Project,
  type Resume,
  type Skill,
} from "@/lib/api";
import FieldList from "@/components/FieldList";
import StatusBadge from "@/components/StatusBadge";
import { ErrorBox, Loading } from "@/components/States";

const WARNINGS: Record<string, string> = {
  little_text_found:
    "Very little text was found. The file may be a scan or an image. Add your details manually below.",
};

function messageOf(e: unknown, fallback: string): string {
  return e instanceof ApiError ? e.message : fallback;
}

function ResumeDetailContent() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [resume, setResume] = useState<Resume | null>(null);
  const [draft, setDraft] = useState<Analysis | null>(null);
  const [dirty, setDirty] = useState(false);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const loadResume = useCallback(async () => {
    try {
      setResume(await api.getResume(id));
      setError(null);
    } catch (e) {
      setError(messageOf(e, "Could not load this resume."));
    }
  }, [id]);

  // Load resume when the page opens or the ID changes.
  useEffect(() => {
    let cancelled = false;

    async function fetchResume() {
      try {
        const data = await api.getResume(id);

        if (!cancelled) {
          setResume(data);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) {
          setError(messageOf(e, "Could not load this resume."));
        }
      }
    }

    fetchResume();

    return () => {
      cancelled = true;
    };
  }, [id]);

  // Poll while the worker is busy.
  const status = resume?.status;

  useEffect(() => {
    if (status !== "uploaded" && status !== "processing") return;

    const timer = setInterval(loadResume, 2000);

    return () => clearInterval(timer);
  }, [status, loadResume]);

  // Load the extracted details once they are ready.
  const ready = status === "needs_review" || status === "completed";

  useEffect(() => {
    if (!ready || draft !== null) return;

    let cancelled = false;

    async function fetchAnalysis() {
      try {
        const a = await api.getAnalysis(id);

        if (!cancelled) {
          setDraft({
            skills: a.skills,
            projects: a.projects,
            experiences: a.experiences,
            education: a.education,
          });
        }
      } catch (e) {
        if (!cancelled) {
          setError(
            messageOf(e, "Could not load the extracted details.")
          );
        }
      }
    }

    fetchAnalysis();

    return () => {
      cancelled = true;
    };
  }, [ready, draft, id]);

  function update<K extends keyof Analysis>(
    key: K,
    value: Analysis[K]
  ) {
    setDraft((d) => (d ? { ...d, [key]: value } : d));
    setDirty(true);
    setNotice(null);
  }

  async function save(): Promise<boolean> {
    if (!draft) return false;

    setWorking(true);
    setError(null);

    try {
      await api.saveAnalysis(id, draft);
      setDirty(false);
      await loadResume();
      return true;
    } catch (e) {
      setError(messageOf(e, "Could not save your changes."));
      return false;
    } finally {
      setWorking(false);
    }
  }

  async function onSave() {
    if (await save()) {
      setNotice("Changes saved. Confirm when everything looks right.");
    }
  }

  async function onConfirm() {
    if (dirty && !(await save())) return;

    setWorking(true);
    setError(null);

    try {
      setResume(await api.confirmResume(id));
      setNotice("Resume confirmed. It can now be used for practice.");
    } catch (e) {
      setError(messageOf(e, "Could not confirm the resume."));
    } finally {
      setWorking(false);
    }
  }

  async function onReprocess() {
    if (!window.confirm("Read the file again? Your edits will be replaced.")) {
      return;
    }

    setWorking(true);
    setError(null);

    try {
      setResume(await api.reprocessResume(id));
      setDraft(null);
      setDirty(false);
      setNotice(null);
    } catch (e) {
      setError(messageOf(e, "Could not restart processing."));
    } finally {
      setWorking(false);
    }
  }

  async function onDelete() {
    if (
      !window.confirm(
        "Delete this resume and all details extracted from it?"
      )
    ) {
      return;
    }

    setWorking(true);

    try {
      await api.deleteResume(id);
      router.push("/resume");
    } catch (e) {
      setError(messageOf(e, "Could not delete the resume."));
      setWorking(false);
    }
  }

  if (!resume && !error) return <Loading />;

  return (
    <div>
      <Link
        href="/resume"
        className="text-sm text-gray-600 hover:underline"
      >
        Back to resumes
      </Link>

      {resume && (
        <div className="mb-4 mt-2 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-semibold">
            {resume.original_filename}
          </h1>
          <StatusBadge status={resume.status} />
        </div>
      )}

      {error && <ErrorBox message={error} />}

      {notice && (
        <p
          role="status"
          className="mb-4 rounded border border-green-300 bg-green-50 p-3 text-green-800"
        >
          {notice}
        </p>
      )}

      {resume &&
        (status === "uploaded" || status === "processing") && (
          <Loading label="Reading your resume. This usually takes a few seconds..." />
        )}

      {resume?.status === "failed" && (
        <div className="mb-4">
          <ErrorBox
            message={resume.status_message ?? "Processing failed."}
          />
        </div>
      )}

      {resume?.status_message && resume.status === "needs_review" && (
        <p className="mb-4 rounded border border-yellow-300 bg-yellow-50 p-3 text-yellow-900">
          {resume.status_message}
        </p>
      )}

      {resume?.extraction_warnings.map((w) => (
        <p key={w} className="mb-2 text-sm text-yellow-800">
          {WARNINGS[w] ?? w}
        </p>
      ))}

      {ready && draft && (
        <>
          <p className="mb-6 text-sm text-gray-600">
            Check what we found. Correct anything that is wrong, add what is missing, then confirm.
          </p>

          <FieldList
            title="Skills"
            items={draft.skills}
            fields={[
              { key: "name", label: "Skill" },
              { key: "category", label: "Category" },
            ]}
            onChange={(items) => update("skills", items as Skill[])}
            addLabel="Add skill"
            max={60}
          />

          <FieldList
            title="Projects"
            items={draft.projects}
            fields={[
              { key: "name", label: "Project name" },
              { key: "technologies", label: "Technologies" },
              {
                key: "description",
                label: "Description",
                multiline: true,
              },
            ]}
            onChange={(items) => update("projects", items as Project[])}
            addLabel="Add project"
            max={15}
          />

          <FieldList
            title="Experience"
            items={draft.experiences}
            fields={[
              { key: "company", label: "Company or organisation" },
              { key: "role", label: "Role" },
              {
                key: "description",
                label: "Description",
                multiline: true,
              },
            ]}
            onChange={(items) =>
              update("experiences", items as Experience[])
            }
            addLabel="Add experience"
            max={15}
          />

          <FieldList
            title="Education"
            items={draft.education}
            fields={[
              { key: "institution", label: "Institution" },
              { key: "degree", label: "Degree" },
              { key: "field", label: "Field of study" },
            ]}
            onChange={(items) =>
              update("education", items as Education[])
            }
            addLabel="Add education"
            max={10}
          />
        </>
      )}

      {resume && (
        <div className="mt-6 flex flex-wrap gap-3 border-t pt-4">
          {ready && (
            <>
              <button
                onClick={onSave}
                disabled={working || !dirty}
                className="rounded border bg-white px-4 py-2 disabled:opacity-50"
              >
                Save changes
              </button>

              <button
                onClick={onConfirm}
                disabled={working || (status === "completed" && !dirty)}
                className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
              >
                {status === "completed" && !dirty
                  ? "Confirmed"
                  : "Confirm details"}
              </button>
            </>
          )}

          {(ready || status === "failed") && (
            <button
              onClick={onReprocess}
              disabled={working}
              className="rounded border bg-white px-4 py-2 disabled:opacity-50"
            >
              Read file again
            </button>
          )}

          <button
            onClick={onDelete}
            disabled={working}
            className="rounded border border-red-300 bg-white px-4 py-2 text-red-700 disabled:opacity-50"
          >
            Delete resume
          </button>
        </div>
      )}
    </div>
  );
}
export default function ResumeDetailPage() {
  return (
    <Suspense fallback={<Loading />}>
      <ResumeDetailContent />
    </Suspense>
  );
}
