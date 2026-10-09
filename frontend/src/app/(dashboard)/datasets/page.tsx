"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import DataTable from "@/components/DataTable";
import type { Dataset } from "@/lib/types";

const LAYER_STYLES: Record<string, string> = {
  BRONZE: "bg-amber-100 text-amber-800",
  SILVER: "bg-slate-200 text-slate-700",
  GOLD: "bg-yellow-100 text-yellow-800",
};

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<Dataset[]>("/datasets").then(setDatasets).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h1 className="text-xl font-semibold mb-6">Datasets</h1>
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      <div className="bg-white rounded-xl border border-slate-200 p-2">
        <DataTable<Dataset>
          rows={datasets}
          emptyMessage="No datasets registered yet — run an ingestion or Spark job first."
          columns={[
            { header: "Name", render: (d) => d.name },
            { header: "Layer", render: (d) => <span className={`px-2 py-0.5 rounded text-xs font-medium ${LAYER_STYLES[d.layer]}`}>{d.layer}</span> },
            { header: "Location", render: (d) => <code className="text-xs">{d.location}</code> },
            { header: "Registered", render: (d) => new Date(d.created_at).toLocaleString() },
          ]}
        />
      </div>
    </div>
  );
}
