# DataPulse — Spark Batch Processing

## Local mode vs. production
`.master("local[*]")` is genuinely real Spark, just not distributed
across machines. Production swaps this ONE line for a cluster URL.

## Dedup tie-breaker subtlety
FULL-load tables (customers, products): tie-break on `ingestion_date`
(created_at never changes across re-extractions). INCREMENTAL tables
(orders, events): tie-break on `created_at`. Picking the wrong one
silently produces stale "current state" data.

## Idempotency: partitionOverwriteMode=dynamic
Overwrites ONLY the partitions present in the DataFrame being written —
not the whole target dataset. Rerunning one tenant's job never touches
another tenant's partitions.
