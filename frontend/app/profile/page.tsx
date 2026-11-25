
"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type ProfileUpdate } from "@/lib/api";
import { ErrorBox, Loading } from "@/components/States";

const EDUCATION = [
  "High school",
  "Diploma",
  "Bachelor's",
  "Master's",
  "PhD",
  "Other",
];

const EXPERIENCE = [
  "Student",
  "Fresher",
  "1-3 years",
  "3-5 years",
  "5+ years",
];

// Form fields are always strings.
// The API may return null, but the UI should use empty strings.
type Form = {
  display_name: string;
  education_level: string;
  target_role: string;
  experience_level: string;
};

const empty: Form = {
  display_name: "",
  education_level: "",
  target_role: "",
  experience_level: "",
};

export default function ProfilePage() {
  const [form, setForm] = useState<Form>(empty);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const u = await api.getMe();

        if (!cancelled) {
          setForm({
            display_name: u.display_name ?? "",
            education_level: u.education_level ?? "",
            target_role: u.target_role ?? "",
            experience_level: u.experience_level ?? "",
          });
        }
      } catch (e) {
        if (!cancelled) {
          setError(
            e instanceof ApiError
              ? e.message
              : "Could not load your profile."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, []);

  function setField(name: keyof Form, value: string) {
    setForm((f) => ({ ...f, [name]: value }));
    setSaved(false);
  }

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    setSaving(true);
    setError(null);

    try {
      const payload: ProfileUpdate = {
        display_name: form.display_name.trim() || null,
        education_level: form.education_level || null,
        target_role: form.target_role.trim() || null,
        experience_level: form.experience_level || null,
      };

      await api.updateMe(payload);
      setSaved(true);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not save your profile."
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Loading />;

  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold">Profile</h1>

      {error && <ErrorBox message={error} />}

      <form onSubmit={onSubmit} className="mt-4 space-y-4">
        <div>
          <label
            htmlFor="name"
            className="mb-1 block text-sm font-medium"
          >
            Display name
          </label>

          <input
            id="name"
            maxLength={100}
            value={form.display_name}
            onChange={(e) =>
              setField("display_name", e.target.value)
            }
            className="w-full rounded border bg-white p-2"
          />
        </div>

        <div>
          <label
            htmlFor="edu"
            className="mb-1 block text-sm font-medium"
          >
            Education level
          </label>

          <select
            id="edu"
            value={form.education_level}
            onChange={(e) =>
              setField("education_level", e.target.value)
            }
            className="w-full rounded border bg-white p-2"
          >
            <option value="">Select...</option>

            {EDUCATION.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="role"
            className="mb-1 block text-sm font-medium"
          >
            Target role
          </label>

          <input
            id="role"
            maxLength={100}
            value={form.target_role}
            onChange={(e) =>
              setField("target_role", e.target.value)
            }
            className="w-full rounded border bg-white p-2"
          />
        </div>

        <div>
          <label
            htmlFor="exp"
            className="mb-1 block text-sm font-medium"
          >
            Experience level
          </label>

          <select
            id="exp"
            value={form.experience_level}
            onChange={(e) =>
              setField("experience_level", e.target.value)
            }
            className="w-full rounded border bg-white p-2"
          >
            <option value="">Select...</option>

            {EXPERIENCE.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save profile"}
        </button>

        {saved && (
          <p role="status" className="text-green-700">
            Profile saved.
          </p>
        )}
      </form>
    </div>
  );
}
