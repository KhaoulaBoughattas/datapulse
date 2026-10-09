# DataPulse — Monitoring

## The /metrics naming collision
`GET /metrics` was originally JSON business metrics (Phase 3). Prometheus
needs plain-text exposition at that same path. Resolution: JSON moved to
`GET /metrics/business`; `GET /metrics` now serves Prometheus format.

## Counter vs. Gauge
- `pipeline_success_total`/`pipeline_failure_total`: Counters (monotonic, `rate()`-friendly).
- `data_quality_score`: Gauge (can legitimately go up or down between runs).
