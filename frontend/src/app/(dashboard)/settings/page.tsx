"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import { useAuth } from "@/lib/auth-context";
import DataTable from "@/components/DataTable";
import RoleGate from "@/components/RoleGate";
import type { CurrentUser } from "@/lib/types";

export default function SettingsPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<CurrentUser[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    api.get<CurrentUser[]>("/users").then(setUsers).catch((e) => setError(e.message));
  }, [user]);

  return (
    <div>
      <h1 className="text-xl font-semibold mb-6">Settings</h1>
      <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6 max-w-md">
        <h2 className="text-sm font-semibold text-slate-700 mb-3">Your Account</h2>
        <dl className="text-sm space-y-1">
          <div className="flex justify-between"><dt className="text-slate-500">Email</dt><dd>{user?.email}</dd></div>
          <div className="flex justify-between"><dt className="text-slate-500">Role</dt><dd>{user?.role}</dd></div>
        </dl>
      </div>
      <RoleGate permission="user:read">
        <h2 className="text-sm font-semibold text-slate-700 mb-2">Team Members</h2>
        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
        <div className="bg-white rounded-xl border border-slate-200 p-2 max-w-2xl">
          <DataTable<CurrentUser>
            rows={users}
            emptyMessage="No other team members yet."
            columns={[
              { header: "Name", render: (u) => u.full_name },
              { header: "Email", render: (u) => u.email },
              { header: "Role", render: (u) => u.role },
              { header: "Active", render: (u) => (u.is_active ? "Yes" : "No") },
            ]}
          />
        </div>
      </RoleGate>
    </div>
  );
}
