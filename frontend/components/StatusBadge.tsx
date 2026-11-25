import type { ResumeStatus } from "@/lib/api";

const LABELS: Record<ResumeStatus, string> = {
  uploaded: "Queued",
  processing: "Reading resume...",
  needs_review: "Needs your review",
  completed: "Confirmed",
  failed: "Failed",
};

const COLORS: Record<ResumeStatus, string> = {
  uploaded: "bg-gray-200 text-gray-800",
  processing: "bg-blue-100 text-blue-800",
  needs_review: "bg-yellow-100 text-yellow-900",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

export default function StatusBadge({ status }: { status: ResumeStatus }) {
  return (
    <span className={`rounded px-2 py-0.5 text-sm font-medium ${COLORS[status]}`}>
      {LABELS[status]}
    </span>
  );
}