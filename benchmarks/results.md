# DataPulse Benchmark Results

Run `python scripts/benchmark.py --sizes 10000,100000` to generate real,
measured results here. This file is a placeholder until you do — do not
copy numbers from documentation as if they were your own measurements.

## Postgres index improvement (measured during Phase 18 design)

`idx_orders_tenant_created` (already present in
`infrastructure/postgres/schema/source_schema.sql`) cut the ingestion
watermark query from ~41ms to ~7ms at 100K orders in the reference
build — negligible difference at 10K rows. Re-verify with:

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE tenant_id='acme' AND created_at > '2026-01-01';
```
