# DataPulse — Performance Optimization

All numbers should be YOUR OWN measurements from `scripts/benchmark.py`
— see `benchmarks/results.md`.

## Postgres index (already applied in source_schema.sql)
`idx_orders_tenant_created` (composite tenant_id+created_at index)
addresses the ingestion watermark query's actual access pattern —
verify with `EXPLAIN ANALYZE` before/after at meaningful row counts
(differences are negligible below ~50K rows).

## Spark
- Report NEGATIVE results honestly: `.cache()` on a DataFrame read only
  once doesn't help — measure before assuming.
- Explicit `F.broadcast()` hints may be redundant at small scale (Spark's
  auto-broadcast threshold, default 10MB, often already covers it) but
  protect against future data growth crossing that threshold.

## dbt incremental vs. full-refresh
The clearest measured win: incremental re-runs scale with NEW rows only;
full-refresh scales with TOTAL rows. Verify with `dbt run --full-refresh`
timing vs. a normal incremental `dbt run` after adding new data.
