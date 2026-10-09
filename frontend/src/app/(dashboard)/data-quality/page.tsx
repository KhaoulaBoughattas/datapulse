"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import DataTable from "@/components/DataTable";
import StatCard from "@/components/StatCard";
import type { QualityResult } from "@/lib/types";

export default function DataQualityPage() {
  const [results, setResults] = useState<QualityResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<QualityResult[]>("/quality").then(setResults).catch((e) => setError(e.message));
  }, []);

  const overall = results.length > 0 ? (results.reduce((s, r) => s + r.score, 0) / results.length).toFixed(1) : null;
  const failedCount = results.filter((r) => !r.passed).length;

  return (
    <div>
      <h1 className="text-xl font-semibold mb-6">Data Quality</h1>
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <StatCard label="Overall Score" value={overall ? `${overall}%` : "—"} />
        <StatCard label="Checks Run" value={`${results.length}`} />
        <StatCard label="Failed Checks" value={`${failedCount}`} />
      </div>
      <div className="bg-white rounded-xl border border-slate-200 p-2">
        <DataTable<QualityResult>
          rows={results}
          emptyMessage="No quality checks have run yet."
          columns={[
            { header: "Status", render: (r) => <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.passed ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{r.passed ? "PASS" : "FAIL"}</span> },
            { header: "Check", render: (r) => <code className="text-xs">{r.check_name}</code> },
            { header: "Score", render: (r) => `${r.score.toFixed(1)}%` },
            { header: "Run At", render: (r) => new Date(r.run_at).toLocaleString() },
          ]}
        />
      </div>
    </div>
  );
}
