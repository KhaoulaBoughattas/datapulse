# ADR 004: Use Apache Airflow for Orchestration

## Context
Need scheduling, retries, and dependency management for ingestion/quality tasks.

## Decision
Apache Airflow, LocalExecutor, its own dedicated Postgres metadata database.

## Alternatives Considered
- Dagster/Prefect: cleaner asset-based models, but Airflow is the most
  commonly asked-about orchestrator in DE interviews.
- Cron + scripts: no retry/dependency semantics, no UI.

## Consequences
Airflow's dependency pins are strict — this project uses Airflow's
official constraints file matched to the exact Python/Airflow version.
