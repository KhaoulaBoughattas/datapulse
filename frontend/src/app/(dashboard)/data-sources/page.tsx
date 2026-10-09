"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import DataTable from "@/components/DataTable";
import RoleGate from "@/components/RoleGate";
import type { DataSource } from "@/lib/types";

export default function DataSourcesPage() {
  const [sources, setSources] = useState<DataSource[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [type, setType] = useState<"POSTGRES" | "REST_API" | "KAFKA">("POSTGRES");
  const [error, setError] = useState<string | null>(null);

  function load() {
    api.get<DataSource[]>("/data-sources").then(setSources).catch((e) => setError(e.message));
  }
  useEffect(load, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/data-sources", { name, source_type: type, connection_config: {} });
      setName("");
      setShowForm(false);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create data source");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold">Data Sources</h1>
        <RoleGate permission="data_source:write">
          <button onClick={() => setShowForm((s) => !s)} className="bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium px-4 py-2 rounded-md">New Data Source</button>
        </RoleGate>
      </div>
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      {showForm && (
        <form onSubmit={handleCreate} className="bg-white border border-slate-200 rounded-xl p-5 mb-6 flex gap-3 items-end">
          <div>
            <label className="block text-xs font-medium mb-1">Name</label>
            <input className="border border-slate-300 rounded-md px-3 py-1.5 text-sm" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1">Type</label>
            <select className="border border-slate-300 rounded-md px-3 py-1.5 text-sm" value={type} onChange={(e) => setType(e.target.value as typeof type)}>
              <option value="POSTGRES">POSTGRES</option>
              <option value="REST_API">REST_API</option>
              <option value="KAFKA">KAFKA</option>
            </select>
          </div>
          <button type="submit" className="bg-slate-900 text-white text-sm px-4 py-1.5 rounded-md">Create</button>
        </form>
      )}
      <div className="bg-white rounded-xl border border-slate-200 p-2">
        <DataTable<DataSource>
          rows={sources}
          emptyMessage="No data sources connected yet."
          columns={[
            { header: "Name", render: (s) => s.name },
            { header: "Type", render: (s) => s.source_type },
            { header: "Created", render: (s) => new Date(s.created_at).toLocaleString() },
          ]}
        />
      </div>
    </div>
  );
}
