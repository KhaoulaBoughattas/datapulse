# DataPulse — dbt Transformations

## Layer responsibilities
- **staging/**: 1:1 typed extraction from RAW — the ONE place backend
  differences (Snowflake VARIANT vs. Postgres typed columns) are
  handled, via `{{ target.type }}`.
- **intermediate/**: reusable business logic shared by multiple marts.
- **marts/**: the star schema + metrics, materialized as tables.

## Why fact_events sources from batch, not streaming
Phase 8's streaming pipeline lands events in a separate bronze path
(`bronze/streaming_events`) from batch's `bronze/events` -> `silver/events`.
The warehouse loader only reads `silver/`, so `fact_events` here reflects
the BATCH path only — an honest, stated scope boundary, not a silent gap.

## Backend portability
| Construct | Snowflake | Postgres fallback |
|---|---|---|
| VARIANT extraction | `_raw_data:col::type` | plain `col` |
| Dedup filter | `qualify row_number() ...` | wrap in a CTE + WHERE instead |
| Date arithmetic | `datediff('day', a, b)` | `b - a` |
| Date functions | `dateadd('minute', 5, current_timestamp())` | `current_timestamp + interval '5 minutes'` |

## Incremental models
`fact_orders` and `fact_events` use `materialized='incremental'` +
`unique_key` + `incremental_strategy='merge'` — MERGE updates existing
rows rather than duplicating them on rerun.
