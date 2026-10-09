# ADR 003: Use Snowflake as the Warehouse (with a Local Fallback)

## Context
Need a warehouse demonstrating dimensional modeling and compute/storage
separation, without requiring paid cloud credentials for every contributor.

## Decision
Snowflake as primary target; dbt's `{{ target.type }}` branching supports
a local Postgres fallback.

## Alternatives Considered
- BigQuery: equally valid; Snowflake's explicit warehouse concept is
  pedagogically clearer.
- Redshift: tightly coupled to AWS.

## Consequences
One dbt project must handle two SQL dialects' differences (documented in
docs/dbt.md) — a real, stated complexity cost for broader runnability.
