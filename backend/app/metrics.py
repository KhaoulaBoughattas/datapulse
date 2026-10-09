"""Prometheus metric definitions, incremented at the exact points in the
code where the underlying events already occur."""
from __future__ import annotations
from prometheus_client import Counter, Gauge, Histogram

pipeline_success_total = Counter("pipeline_success_total", "Total pipeline runs that finished SUCCESS", ["tenant_id", "pipeline_name"])
pipeline_failure_total = Counter("pipeline_failure_total", "Total pipeline runs that finished FAILED", ["tenant_id", "pipeline_name"])
pipeline_duration_seconds = Histogram("pipeline_duration_seconds", "Pipeline run duration in seconds", ["tenant_id", "pipeline_name"], buckets=[1, 5, 15, 30, 60, 120, 300, 600, 1800])
records_processed_total = Counter("records_processed_total", "Total records processed across all pipeline runs", ["tenant_id", "pipeline_name"])
data_quality_score = Gauge("data_quality_score", "Most recent data quality score per check", ["tenant_id", "check_name"])
