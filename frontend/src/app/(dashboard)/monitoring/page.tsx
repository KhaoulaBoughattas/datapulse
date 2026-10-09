export default function MonitoringPage() {
  const links = [
    { label: "Grafana — Pipeline Health", url: "http://localhost:3001/d/datapulse-pipeline-health" },
    { label: "Grafana — Kafka", url: "http://localhost:3001/d/datapulse-kafka" },
    { label: "Grafana — Spark Streaming", url: "http://localhost:3001/d/datapulse-spark-streaming" },
    { label: "Grafana — Data Quality", url: "http://localhost:3001/d/datapulse-data-quality" },
    { label: "Prometheus", url: "http://localhost:9090" },
    { label: "Airflow", url: "http://localhost:8080" },
    { label: "Kafka UI", url: "http://localhost:8081" },
    { label: "MinIO Console", url: "http://localhost:9001" },
  ];
  return (
    <div>
      <h1 className="text-xl font-semibold mb-1">Monitoring</h1>
      <p className="text-sm text-slate-500 mb-6">Real-time metrics live in Grafana/Prometheus — this page is a deep-link hub.</p>
      <div className="grid grid-cols-2 gap-4">
        {links.map((l) => (
          <a key={l.url} href={l.url} target="_blank" rel="noreferrer" className="bg-white border border-slate-200 rounded-xl p-4 text-sm font-medium text-brand-600 hover:border-brand-300">{l.label} ↗</a>
        ))}
      </div>
    </div>
  );
}
