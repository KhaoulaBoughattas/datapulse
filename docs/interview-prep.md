# DataPulse — Interview Preparation Guide

## Kafka
**Q: How do you guarantee ordering in Kafka?**
A: Only within a partition. Events keyed by customer_id so one
customer's events land on the same partition, in order. Tradeoff: hot
partitions for very active keys.

**Q: What does an idempotent producer protect against?**
A: Broker-side duplicate writes from producer retries within ONE
session — not crashes/restarts, not consumer-side duplicates.

## Spark
**Q: How do you dedupe a stream without unbounded memory?**
A: `dropDuplicatesWithinWatermark` — state expires once a key's
timestamp falls further behind the max-seen-timestamp than the watermark.

**Q: What does "exactly-once" mean in Structured Streaming?**
A: At-least-once delivery + idempotent processing + idempotent sink,
composed — not a single setting.

## dbt / Warehouse
**Q: How does an incremental model avoid duplicating rows?**
A: `unique_key` + `incremental_strategy='merge'` — updates existing
rows rather than inserting duplicates.

**Q: Why land RAW as semi-structured?**
A: Isolates schema drift to the transformation layer (dbt), which fails
visibly and diagnosably, rather than breaking the load step itself.

## Idempotency (end to end)
Three mechanisms at three stages: (1) ingestion watermarks advance to
the max OBSERVED value, never wall-clock now(); (2) partition overwrite
(delete-then-put / Spark dynamic partition overwrite); (3) dbt MERGE by
unique_key.

## Multi-tenancy and Security
**Q: Why both app-layer isolation AND database RLS?**
A: Different failure classes. App-layer covers the ORM code path but
depends on every repository remembering to filter. RLS is enforced by
Postgres regardless — catches raw SQL, forgotten filters, admin queries.

**Q: A real, honest limitation in this design?**
A: API keys authenticate as the tenant OWNER — full permissions, not a
scoped subset yet.

## AWS / Terraform
**Q: Why private subnets for RDS/ECS but public for ALB only?**
A: Minimum necessary exposure.

**Q: Why does Terraform CI never run apply?**
A: plan/apply separation prevents a bad PR from provisioning/destroying
real infra before human review.

## What you should be able to explain before putting this on a CV
- Every idempotency mechanism above, from memory.
- The precise difference between what app-layer and RLS isolation each catch.
- The scope boundary between batch and streaming event paths.
- Why each major technology was chosen, and the strongest alternative you didn't pick.
