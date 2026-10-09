# DataPulse — Data Lineage

## Two composed layers
1. Automatic (Spark listener via `spark.extraListeners`): captures
   dataset-level read/write lineage from Spark's own execution plan.
2. Explicit (`lineage/emitter.py`): adds DataPulse-specific context
   (tenant, pipeline name) the Spark listener can't know about.

## Why GET /lineage exists alongside Marquez's own UI
Marquez has no tenant/RBAC concept. `_tenant_matches()` filters job/
dataset names by a naming convention (`job.tenant_slug`) on the way out
— the enforcement point that makes `/lineage` safe to expose per-tenant.
