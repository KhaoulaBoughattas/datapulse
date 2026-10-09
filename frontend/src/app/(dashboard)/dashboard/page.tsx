"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import StatCard from "@/components/StatCard";
import type { BusinessMetrics, QualityResult } from "@/lib/types";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<BusinessMetrics | null>(null);
  const [quality, setQuality] = useState<QualityResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.get<BusinessMetrics>("/metrics/business"), api.get<QualityResult[]>("/quality")])
      .then(([m, q]) => {
        setMetrics(m);
        setQuality(q);
      })
      .catch((e) => setError(e.message));
  }, []);

  const avgQuality = quality.length > 0 ? (quality.reduce((sum, q) => sum + q.score, 0) / quality.length).toFixed(1) : null;

  return (
    <div>
      <h1 className="text-xl font-semibold mb-6">Dashboard</h1>
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard label="Active Pipelines" value={metrics ? `${metrics.active_pipelines}` : "…"} />
        <StatCard label="Success Rate" value={metrics?.pipeline_success_rate != null ? `${(metrics.pipeline_success_rate * 100).toFixed(1)}%` : "—"} hint={metrics?.total_pipeline_runs ? `${metrics.total_pipeline_runs} runs` : "No runs yet"} />
        <StatCard label="Records Processed" value={metrics ? metrics.total_records_processed.toLocaleString() : "…"} />
        <StatCard label="Data Quality Score" value={avgQuality ? `${avgQuality}%` : "—"} hint={quality.length ? `${quality.length} checks` : "No checks run yet"} />
        <StatCard label="Kafka Lag" value="See Grafana" hint="Live lag is a Prometheus/Grafana metric" />
      </div>
    </div>
  );
}
