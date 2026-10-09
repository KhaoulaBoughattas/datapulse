# DataPulse — Airflow Orchestration (Phase 5)

## Why Airflow has its own Postgres

Airflow's metadata DB (DAG run history, task state) is operational
metadata about the orchestrator — unrelated to `datapulse`/
`datapulse_source`. Keeping it separate means an Airflow upgrade never
touches product data.

## Retry vs. fail-fast

`airflow/dags/common/error_handling.py`'s `fail_fast_on_data_errors`
decorator catches schema/data exceptions (`ProgrammingError`,
`ValueError`, etc.) and re-raises as `AirflowFailException` — NO retry,
since identical bad input produces identical failure. Everything else
(network timeouts) propagates normally and IS retried via the task's
`retries`/`retry_delay` config.

## Running it

```powershell
docker compose up -d --build airflow-postgres airflow-init airflow-webserver airflow-scheduler
docker compose ps
```

Wait for `airflow-init` to show `Exited (0)` (one-shot setup, success =
exit code 0), then `airflow-webserver`/`airflow-scheduler` should show
`Up (healthy)` / `Up`.

Open http://localhost:8080 (admin/admin), find `daily_source_ingestion`,
un-pause it, and trigger manually via the ▶ button, or:

```powershell
docker exec -it datapulse-airflow-webserver airflow dags trigger daily_source_ingestion
```

## Known gotcha specific to this phase

The DAG's service account login (`DATAPULSE_DAG_SERVICE_EMAIL`,
default `owner@acme.io`) must match a REAL user you've already
registered via `POST /auth/register` — the DAG does not create the
tenant/user itself. Register `acme` / `owner@acme.io` /
`supersecret123` (per the Phase 3/4 README steps) before triggering
this DAG.
