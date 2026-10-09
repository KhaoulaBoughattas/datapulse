"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api-client";
import DataTable from "@/components/DataTable";
import type { Pipeline, PipelineRun } from "@/lib/types";

const STATUS_STYLES: Record<string, string> = {
  SUCCESS: "bg-green-100 text-green-700",
  FAILED: "bg-red-100 text-red-700",
  RUNNING: "bg-amber-100 text-amber-700",
};

export default function PipelineDetailPage() {
  const params = useParams<{ id: string }>();
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.get<Pipeline>(`/pipelines/${params.id}`), api.get<PipelineRun[]>(`/pipeline-runs?pipeline_id=${params.id}`)])
      .then(([p, r]) => {
        setPipeline(p);
        setRuns(r);
      })
      .catch((e) => setError(e.message));
  }, [params.id]);

  if (error) return <p className="text-red-600 text-sm">{error}</p>;
  if (!pipeline) return <p className="text-slate-400 text-sm">Loading…</p>;

  return (
    <div>
      <h1 className="text-xl font-semibold mb-1">{pipeline.name}</h1>
      <p className="text-sm text-slate-500 mb-6">{pipeline.pipeline_type} · {pipeline.schedule || "no schedule"}</p>
      <h2 className="text-sm font-semibold text-slate-700 mb-2">Run History</h2>
      <div className="bg-white rounded-xl border border-slate-200 p-2">
        <DataTable<PipelineRun>
          rows={runs}
          emptyMessage="No runs recorded yet for this pipeline."
          columns={[
            { header: "Status", render: (r) => <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_STYLES[r.status]}`}>{r.status}</span> },
            { header: "Started", render: (r) => new Date(r.started_at).toLocaleString() },
            { header: "Finished", render: (r) => (r.finished_at ? new Date(r.finished_at).toLocaleString() : "—") },
            { header: "Records", render: (r) => r.records_processed.toLocaleString() },
            { header: "Error", render: (r) => r.error_message || "—" },
          ]}
        />
      </div>
    </div>
  );
}
