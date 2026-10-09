"""
DataPulse — Daily Source Ingestion DAG.

Orchestrates ingestion/ (Phase 4) on a daily schedule, with retries on
transient failures, fail-fast on data errors, and pipeline-run lifecycle
tracking via the DataPulse API.

Dependency shape:
    start_run
      -> [extract_customers, extract_products]   (parallel, independent)
      -> extract_orders
      -> [extract_order_items, extract_payments]  (parallel siblings of orders)
      -> extract_subscriptions
      -> extract_events
      -> run_quality_checks   (light bronze-shape check — see docstring below)
      -> finish_run
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import date, datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, "/opt/airflow")

from common.api_helpers import (  # noqa: E402
    finish_pipeline_run,
    get_or_create_pipeline,
    get_service_token,
    start_pipeline_run,
)
from common.error_handling import fail_fast_on_data_errors  # noqa: E402

from ingestion.config import INGESTION_REGISTRY, load_config  # noqa: E402
from ingestion.extractors import commit_watermark, extract_table, get_source_engine  # noqa: E402
from ingestion.s3_client import ensure_bucket_exists  # noqa: E402
from ingestion.writer import write_bronze_partition  # noqa: E402

logger = logging.getLogger("airflow.task")

TENANT_SLUG = os.getenv("DATAPULSE_DAG_TENANT_SLUG", "acme")
SERVICE_EMAIL = os.getenv("DATAPULSE_DAG_SERVICE_EMAIL", "owner@acme.io")
SERVICE_PASSWORD = os.getenv("DATAPULSE_DAG_SERVICE_PASSWORD", "supersecret123")

TABLE_ORDER = ["customers", "products", "orders", "order_items", "payments", "subscriptions", "events"]
SPEC_BY_TABLE = {spec.table_name: spec for spec in INGESTION_REGISTRY}

default_args = {
    "owner": "data-engineering",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
}


@fail_fast_on_data_errors
def _extract_one_table(table_name: str, **context) -> int:
    config = load_config()
    ensure_bucket_exists(config)
    engine = get_source_engine(config)
    spec = SPEC_BY_TABLE[table_name]

    result = extract_table(engine, TENANT_SLUG, spec)
    write_bronze_partition(config, table_name, TENANT_SLUG, result.dataframe, date.today())

    if result.new_watermark is not None:
        commit_watermark(engine, TENANT_SLUG, table_name, result.new_watermark)

    logger.info("Extracted %d rows for %s.%s", result.row_count, TENANT_SLUG, table_name)
    return result.row_count


def _start_run(**context) -> None:
    token = get_service_token(TENANT_SLUG, SERVICE_EMAIL, SERVICE_PASSWORD)
    pipeline_id = get_or_create_pipeline(token, "daily_source_ingestion", "BATCH")
    run_id = start_pipeline_run(token, pipeline_id)
    context["ti"].xcom_push(key="token", value=token)
    context["ti"].xcom_push(key="run_id", value=run_id)
    logger.info("Started pipeline run %s for pipeline %s", run_id, pipeline_id)


def _run_bronze_shape_check(**context) -> None:
    """Light bronze-level check: expected columns present, required
    fields non-null. Uniqueness/referential checks are deliberately NOT
    run here — bronze can legitimately contain duplicate snapshots
    across ingestion_date partitions for FULL-load tables before Spark
    dedupes them (Phase 6). The full Great Expectations suite (Phase 11)
    runs against SILVER separately."""
    logger.info("Bronze shape check: (stub) — full implementation lands with Phase 11's data_quality package.")


def _finish_run(**context) -> None:
    ti = context["ti"]
    token = ti.xcom_pull(task_ids="start_run", key="token")
    run_id = ti.xcom_pull(task_ids="start_run", key="run_id")

    total_records = 0
    for table_name in TABLE_ORDER:
        count = ti.xcom_pull(task_ids=f"extract_{table_name}")
        total_records += count or 0

    dag_run = context["dag_run"]
    failed_tasks = [t.task_id for t in dag_run.get_task_instances() if t.task_id.startswith("extract_") and t.state == "failed"]

    if failed_tasks:
        finish_pipeline_run(token, run_id, status="FAILED", records_processed=total_records, error_message=f"Tasks failed: {failed_tasks}")
        raise Exception(f"Upstream extraction tasks failed: {failed_tasks}")

    finish_pipeline_run(token, run_id, status="SUCCESS", records_processed=total_records)
    logger.info("Pipeline run %s finished SUCCESS, %d total records", run_id, total_records)


with DAG(
    dag_id="daily_source_ingestion",
    description="Extracts datapulse_source tables into the S3/MinIO bronze layer",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ingestion", "bronze"],
) as dag:
    start_run = PythonOperator(task_id="start_run", python_callable=_start_run)

    extract_tasks = {
        table_name: PythonOperator(task_id=f"extract_{table_name}", python_callable=_extract_one_table, op_kwargs={"table_name": table_name})
        for table_name in TABLE_ORDER
    }

    quality_checks = PythonOperator(task_id="run_quality_checks", python_callable=_run_bronze_shape_check)
    finish_run = PythonOperator(task_id="finish_run", python_callable=_finish_run, trigger_rule="all_done")

    start_run >> [extract_tasks["customers"], extract_tasks["products"]]
    [extract_tasks["customers"], extract_tasks["products"]] >> extract_tasks["orders"]
    extract_tasks["orders"] >> [extract_tasks["order_items"], extract_tasks["payments"]]
    [extract_tasks["order_items"], extract_tasks["payments"]] >> extract_tasks["subscriptions"]
    extract_tasks["subscriptions"] >> extract_tasks["events"]
    extract_tasks["events"] >> quality_checks >> finish_run
