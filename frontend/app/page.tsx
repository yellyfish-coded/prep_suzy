"use client";

import { useEffect, useState } from "react";
import { api, type User } from "@/lib/api";
import { ErrorBox, Loading } from "@/components/States";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getMe()
      .then(setUser)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <ErrorBox message={error} />;
  if (!user) return <Loading />;

  return (
    <div>
      <h1 className="mb-2 text-2xl font-semibold">Welcome, {user.display_name ?? "student"}</h1>
      <p className="text-gray-600">
        Your dashboard will show practice progress here once sessions are built (Phase 7).
      </p>
    </div>
  );
}