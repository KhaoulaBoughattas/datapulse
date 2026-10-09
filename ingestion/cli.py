#!/usr/bin/env python
"""
DataPulse ingestion CLI.

Usage:
    python -m ingestion.cli --tenant acme
    python -m ingestion.cli --all-tenants
"""
from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timezone
from uuid import UUID

from dotenv import load_dotenv
from sqlalchemy import text

from ingestion.api_client import DataPulseApiClient
from ingestion.config import INGESTION_REGISTRY, LoadStrategy, load_config
from ingestion.extractors import commit_watermark, extract_table, get_source_engine
from ingestion.s3_client import ensure_bucket_exists
from ingestion.writer import write_bronze_partition

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("ingestion.cli")


def _all_tenant_ids(engine) -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT tenant_id FROM tenants ORDER BY tenant_id")).fetchall()
    return [r[0] for r in rows]


def run_ingestion(tenant_ids, table_filter, api_client) -> dict[str, int]:
    config = load_config()
    ensure_bucket_exists(config)
    engine = get_source_engine(config)

    pipeline_id = None
    if api_client is not None:
        pipeline_id = api_client.get_or_create_pipeline("postgres_bronze_ingestion", "BATCH")

    totals: dict[str, int] = {}
    today = datetime.now(timezone.utc).date()

    specs = INGESTION_REGISTRY
    if table_filter:
        specs = [s for s in specs if s.table_name == table_filter]
        if not specs:
            raise SystemExit(f"Unknown table '{table_filter}'.")

    for tenant_id in tenant_ids:
        for spec in specs:
            result = extract_table(engine, tenant_id, spec)
            location = write_bronze_partition(config, spec.table_name, tenant_id, result.dataframe, today)
            totals[f"{tenant_id}.{spec.table_name}"] = result.row_count

            if spec.strategy == LoadStrategy.INCREMENTAL and result.new_watermark is not None:
                commit_watermark(engine, tenant_id, spec.table_name, result.new_watermark)

            if api_client is not None and pipeline_id is not None:
                api_client.register_dataset(name=spec.table_name, layer="BRONZE", location=location, pipeline_id=pipeline_id)

    return totals


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="DataPulse PostgreSQL -> S3/MinIO bronze ingestion")
    parser.add_argument("--tenant", type=str)
    parser.add_argument("--all-tenants", action="store_true")
    parser.add_argument("--table", type=str, default=None)
    parser.add_argument("--api-token", type=str, default=None)
    parser.add_argument("--api-base-url", type=str, default="http://localhost:8000")
    args = parser.parse_args()

    if not args.tenant and not args.all_tenants:
        parser.error("Provide --tenant <slug> or --all-tenants")

    config = load_config()
    engine = get_source_engine(config)
    tenant_ids = _all_tenant_ids(engine) if args.all_tenants else [args.tenant]

    api_client = DataPulseApiClient(args.api_base_url, args.api_token) if args.api_token else None

    logger.info("Starting ingestion: tenants=%s table_filter=%s", tenant_ids, args.table)
    start = time.perf_counter()
    try:
        totals = run_ingestion(tenant_ids, args.table, api_client)
    finally:
        if api_client is not None:
            api_client.close()
    elapsed = time.perf_counter() - start

    logger.info("=" * 60)
    logger.info("INGESTION COMPLETE (%.1fs)", elapsed)
    for key, count in totals.items():
        logger.info("  %-30s %10s rows", key, f"{count:,}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
