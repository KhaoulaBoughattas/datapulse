from __future__ import annotations

import logging
import os
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as PGConnection

logger = logging.getLogger("data_generator.db")

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = _REPO_ROOT / "infrastructure" / "postgres" / "schema" / "source_schema.sql"

_TABLES_IN_DROP_ORDER = [
    "events", "subscriptions", "payments", "order_items", "orders", "products", "customers", "tenants",
]


def get_connection() -> PGConnection:
    required = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}. Did you copy .env.example to .env?")

    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.getenv("POSTGRES_SOURCE_DB", "datapulse_source"),
    )


def reset_schema(conn: PGConnection) -> None:
    logger.warning("Resetting source schema (dropping %d tables)...", len(_TABLES_IN_DROP_ORDER))
    with conn.cursor() as cur:
        for table in _TABLES_IN_DROP_ORDER:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    conn.commit()


def apply_schema(conn: PGConnection) -> None:
    sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    logger.info("Source schema applied from %s", _SCHEMA_PATH)
