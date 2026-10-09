#!/usr/bin/env python
"""
DataPulse — Bronze to Silver batch job.

Usage:
    python jobs/batch/bronze_to_silver.py --tenant acme
    python jobs/batch/bronze_to_silver.py --all-tenants --api-token <token>
"""
from __future__ import annotations
import argparse
import logging
import os
import sys

from dotenv import load_dotenv
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

sys.path.insert(0, "/opt/app")

from ingestion.api_client import DataPulseApiClient  # noqa: E402
from jobs.batch.common.schemas import SILVER_TABLE_SPECS, SilverTableSpec  # noqa: E402
from jobs.batch.common.spark_session import bucket_path, get_spark_session  # noqa: E402
from jobs.batch.common.tenants import list_tenant_ids  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("bronze_to_silver")


def cast_to_canonical_schema(df: DataFrame, spec: SilverTableSpec) -> DataFrame:
    missing = [c.name for c in spec.columns if c.name not in df.columns]
    if missing:
        raise ValueError(f"[{spec.table_name}] Missing expected column(s) in bronze data: {missing}.")
    return df.select(*[F.col(c.name).cast(c.dtype).alias(c.name) for c in spec.columns])


def dedup_by_primary_key(df: DataFrame, spec: SilverTableSpec, tie_breaker_col: str) -> DataFrame:
    window = Window.partitionBy(spec.primary_key).orderBy(F.col(tie_breaker_col).desc())
    return df.withColumn("_row_num", F.row_number().over(window)).filter(F.col("_row_num") == 1).drop("_row_num")


def process_table(spark, bucket: str, tenant_id: str, spec: SilverTableSpec) -> int:
    bronze_path = bucket_path(bucket, "bronze", spec.table_name, f"tenant_id={tenant_id}")
    raw_df = spark.read.parquet(bronze_path)

    if raw_df.rdd.isEmpty():
        logger.warning("[%s] No bronze data found at %s — skipping.", tenant_id, bronze_path)
        return 0

    typed_df = cast_to_canonical_schema(raw_df, spec)
    typed_df = typed_df.withColumn("ingestion_date", raw_df["ingestion_date"])
    deduped_df = dedup_by_primary_key(typed_df, spec, spec.dedup_order_column)

    if spec.derived_partition_column and spec.derive_from_column:
        deduped_df = deduped_df.withColumn(spec.derived_partition_column, F.date_format(F.col(spec.derive_from_column), "yyyy-MM"))

    if "ingestion_date" in deduped_df.columns:
        deduped_df = deduped_df.drop("ingestion_date")

    partition_cols = ["tenant_id"] + ([spec.derived_partition_column] if spec.derived_partition_column else [])
    silver_path = bucket_path(bucket, "silver", spec.table_name)

    row_count = deduped_df.count()
    deduped_df.write.mode("overwrite").partitionBy(*partition_cols).parquet(silver_path)
    logger.info("[%s] Wrote %d deduplicated rows to %s", tenant_id, row_count, silver_path)
    return row_count


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Bronze -> Silver batch processing")
    parser.add_argument("--tenant", type=str)
    parser.add_argument("--all-tenants", action="store_true")
    parser.add_argument("--api-token", type=str, default=None)
    parser.add_argument("--api-base-url", type=str, default=os.getenv("DATAPULSE_API_BASE_URL", "http://backend:8000"))
    args = parser.parse_args()

    if not args.tenant and not args.all_tenants:
        parser.error("Provide --tenant <slug> or --all-tenants")

    bucket = os.environ["S3_BUCKET"]
    tenant_ids = list_tenant_ids() if args.all_tenants else [args.tenant]

    api_client = DataPulseApiClient(args.api_base_url, args.api_token) if args.api_token else None
    pipeline_id = None
    run_id = None
    total_rows = 0

    spark = get_spark_session("bronze_to_silver")
    try:
        if api_client:
            pipeline_id = api_client.get_or_create_pipeline("bronze_to_silver_batch", "BATCH")
            run_id = api_client.start_pipeline_run(pipeline_id)

        for tenant_id in tenant_ids:
            for spec in SILVER_TABLE_SPECS:
                row_count = process_table(spark, bucket, tenant_id, spec)
                total_rows += row_count
                if api_client and pipeline_id and row_count > 0:
                    location = bucket_path(bucket, "silver", spec.table_name) + f"/tenant_id={tenant_id}/"
                    api_client.register_dataset(name=f"silver_{spec.table_name}", layer="SILVER", location=location, pipeline_id=pipeline_id)

        if api_client and run_id:
            api_client.finish_pipeline_run(run_id, status="SUCCESS", records_processed=total_rows)

        logger.info("=" * 60)
        logger.info("BRONZE -> SILVER COMPLETE — %d total rows written", total_rows)

    except Exception as exc:
        if api_client and run_id:
            api_client.finish_pipeline_run(run_id, status="FAILED", records_processed=total_rows, error_message=str(exc))
        raise
    finally:
        spark.stop()
        if api_client:
            api_client.close()


if __name__ == "__main__":
    main()
