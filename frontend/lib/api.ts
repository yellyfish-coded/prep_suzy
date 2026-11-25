const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type User = {
  id: string;
  email: string;
  display_name: string | null;
  education_level: string | null;
  target_role: string | null;
  experience_level: string | null;
  created_at: string;
};

export type ProfileUpdate = {
  display_name?: string | null;
  education_level?: string | null;
  target_role?: string | null;
  experience_level?: string | null;
};

export type ResumeStatus = "uploaded" | "processing" | "needs_review" | "completed" | "failed";

export type Resume = {
  id: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: ResumeStatus;
  status_message: string | null;
  extraction_warnings: string[];
  created_at: string;
  updated_at: string;
};

export type Skill = { name: string; category: string; evidence: string };
export type Project = { name: string; description: string; technologies: string };
export type Experience = { company: string; role: string; description: string };
export type Education = { institution: string; degree: string; field: string };

export type Analysis = {
  skills: Skill[];
  projects: Project[];
  experiences: Experience[];
  education: Education[];
};
export type AnalysisOut = Analysis & { is_confirmed: boolean };

type FieldDetail = { field: string; message: string };
type ErrorBody = { error?: { code?: string; message?: string; details?: FieldDetail[] } };

export class ApiError extends Error {
  status: number;
  code: string;
  details?: FieldDetail[];

  constructor(status: number, code: string, message: string, details?: FieldDetail[]) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const isForm = options.body instanceof FormData;
  const headers: Record<string, string> = isForm ? {} : { "Content-Type": "application/json" };

  let res: Response;
  try {
    res = await fetch(`${API_URL}/api/v1${path}`, {
      ...options,
      credentials: "include",
      cache: "no-store",
      headers,
    });
  } catch {
    throw new ApiError(0, "NETWORK_ERROR", "Cannot reach the server. Is the backend running?");
  }

  if (!res.ok) {
    let body: ErrorBody = {};
    try {
      body = (await res.json()) as ErrorBody;
    } catch {
      // response was not JSON
    }
    const details = body.error?.details;
    const detailText = details?.length ? ` (${details.map((d) => `${d.field}: ${d.message}`).join("; ")})` : "";
    throw new ApiError(
      res.status,
      body.error?.code ?? "UNKNOWN_ERROR",
      (body.error?.message ?? "Something went wrong.") + detailText,
      details,
    );
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  getMe: () => request<User>("/users/me"),
  updateMe: (data: ProfileUpdate) =>
    request<User>("/users/me", { method: "PATCH", body: JSON.stringify(data) }),

  listResumes: () => request<Resume[]>("/resumes"),
  getResume: (id: string) => request<Resume>(`/resumes/${id}`),
  uploadResume: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<Resume>("/resumes", { method: "POST", body: form });
  },
  getAnalysis: (id: string) => request<AnalysisOut>(`/resumes/${id}/analysis`),
  saveAnalysis: (id: string, data: Analysis) =>
    request<AnalysisOut>(`/resumes/${id}/analysis`, { method: "PUT", body: JSON.stringify(data) }),
  confirmResume: (id: string) => request<Resume>(`/resumes/${id}/confirm`, { method: "POST" }),
  reprocessResume: (id: string) => request<Resume>(`/resumes/${id}/reprocess`, { method: "POST" }),
  deleteResume: (id: string) => request<void>(`/resumes/${id}`, { method: "DELETE" }),
};