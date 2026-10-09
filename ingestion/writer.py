from __future__ import annotations

import io
import logging
from datetime import date

import pandas as pd
from ingestion.config import IngestionConfig
from ingestion.s3_client import get_s3_client

logger = logging.getLogger("ingestion.writer")


def _partition_prefix(table_name: str, tenant_id: str, ingestion_date: date) -> str:
    return f"bronze/{table_name}/tenant_id={tenant_id}/ingestion_date={ingestion_date.isoformat()}/"


def write_bronze_partition(config: IngestionConfig, table_name: str, tenant_id: str, df: pd.DataFrame, ingestion_date: date) -> str:
    client = get_s3_client(config)
    prefix = _partition_prefix(table_name, tenant_id, ingestion_date)

    existing = client.list_objects_v2(Bucket=config.s3_bucket, Prefix=prefix)
    for obj in existing.get("Contents", []):
        client.delete_object(Bucket=config.s3_bucket, Key=obj["Key"])

    if df.empty:
        logger.info("No rows to write for %s (tenant=%s, date=%s) — skipping.", table_name, tenant_id, ingestion_date)
        return f"s3://{config.s3_bucket}/{prefix}"

    buffer = io.BytesIO()
    df.to_parquet(buffer, engine="pyarrow", index=False, compression="snappy")
    buffer.seek(0)

    key = f"{prefix}part-0000.parquet"
    client.put_object(Bucket=config.s3_bucket, Key=key, Body=buffer.getvalue())
    logger.info("Wrote %d rows to s3://%s/%s", len(df), config.s3_bucket, key)
    return f"s3://{config.s3_bucket}/{prefix}"
