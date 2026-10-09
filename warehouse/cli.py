#!/usr/bin/env python
"""Warehouse loader CLI — loads silver-layer data into RAW.

Usage:
    python -m warehouse.cli --tenant acme
    WAREHOUSE_BACKEND=postgres_local python -m warehouse.cli --tenant acme
"""
from __future__ import annotations
import argparse
import logging
import os
import time
import psycopg2
from dotenv import load_dotenv
from warehouse.config import TABLES, load_postgres_warehouse_config, load_s3_config, load_snowflake_config, resolve_backend
from warehouse.s3_reader import read_silver_table

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("warehouse.cli")


def _all_tenant_ids() -> list[str]:
    conn = psycopg2.connect(host=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"], user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"], dbname=os.getenv("POSTGRES_SOURCE_DB", "datapulse_source"))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT tenant_id FROM tenants ORDER BY tenant_id;")
            return [r[0] for r in cur.fetchall()]
    finally:
        conn.close()


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Load silver data into the RAW warehouse layer")
    parser.add_argument("--tenant", type=str)
    parser.add_argument("--all-tenants", action="store_true")
    parser.add_argument("--table", type=str, default=None)
    args = parser.parse_args()

    if not args.tenant and not args.all_tenants:
        parser.error("Provide --tenant <slug> or --all-tenants")

    backend = resolve_backend()
    logger.info("Warehouse backend: %s", backend)

    s3_config = load_s3_config()
    tenant_ids = _all_tenant_ids() if args.all_tenants else [args.tenant]
    tables = [args.table] if args.table else TABLES

    conn = engine = None
    if backend == "snowflake":
        from warehouse.snowflake_loader import get_connection, load_table as sf_load_table
        conn = get_connection(load_snowflake_config())
    else:
        from warehouse.postgres_loader import get_warehouse_engine, load_table as pg_load_table
        engine = get_warehouse_engine(load_postgres_warehouse_config())

    start = time.perf_counter()
    total_rows = 0
    try:
        for tenant_id in tenant_ids:
            for table_name in tables:
                df = read_silver_table(s3_config, table_name, tenant_id)
                if df.empty:
                    logger.warning("[%s] No silver data for '%s' — skipping.", tenant_id, table_name)
                    continue
                if backend == "snowflake":
                    total_rows += sf_load_table(conn, table_name, df)
                else:
                    total_rows += pg_load_table(engine, table_name, df)
    finally:
        if conn is not None:
            conn.close()

    elapsed = time.perf_counter() - start
    logger.info("WAREHOUSE LOAD COMPLETE (%.1fs) — %d total rows", elapsed, total_rows)


if __name__ == "__main__":
    main()
