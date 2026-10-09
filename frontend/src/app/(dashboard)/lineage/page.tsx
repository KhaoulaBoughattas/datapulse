"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import type { LineageGraph } from "@/lib/types";

export default function LineagePage() {
  const [graph, setGraph] = useState<LineageGraph | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<LineageGraph>("/lineage").then(setGraph).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h1 className="text-xl font-semibold mb-1">Data Lineage</h1>
      <p className="text-sm text-slate-500 mb-6">
        For a full interactive graph, open <a className="text-brand-600 hover:underline" href="http://localhost:3002" target="_blank" rel="noreferrer">Marquez</a>.
      </p>
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      {!graph && !error && <p className="text-slate-400 text-sm">Loading…</p>}
      {graph && graph.nodes.length === 0 && <p className="text-slate-400 text-sm">No lineage recorded yet — run a Spark batch job to generate some.</p>}
      {graph && graph.nodes.length > 0 && (
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h2 className="text-sm font-semibold text-slate-700 mb-2">Datasets</h2>
            <ul className="space-y-1">
              {graph.nodes.filter((n) => n.node_type === "dataset").map((n) => (
                <li key={n.id} className="bg-white border border-slate-200 rounded-md px-3 py-2 text-sm">{n.name}</li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-700 mb-2">Jobs</h2>
            <ul className="space-y-1">
              {graph.nodes.filter((n) => n.node_type === "job").map((n) => (
                <li key={n.id} className="bg-white border border-slate-200 rounded-md px-3 py-2 text-sm">{n.name}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
