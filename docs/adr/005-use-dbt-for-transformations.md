# ADR 005: Use dbt for Transformations

## Context
Need version-controlled, tested, documented SQL transformations from RAW
into a dimensional model.

## Decision
dbt-core, targeting either Snowflake or the local Postgres fallback.

## Alternatives Considered
- Hand-written SQL via Airflow: no built-in testing/docs/dependency graph.
- All transformation in Spark: viable for bronze->silver->gold, but SQL
  inside the warehouse's own compute is standard once data has landed in RAW.

## Consequences
Incremental models required understanding merge-strategy semantics
precisely — a real, demonstrable skill.
