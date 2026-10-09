"""
Smoke test: verifies both DataPulse Postgres databases are reachable.
Run after `docker compose up -d`.

    python scripts/smoke_test_db.py
"""
from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass

import psycopg2
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("smoke_test_db")


@dataclass(frozen=True)
class DbTarget:
    label: str
    dbname: str


def load_config() -> dict[str, str]:
    load_dotenv()
    required = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        logger.error("Missing required environment variable(s): %s. Did you copy .env.example to .env ?", ", ".join(missing))
        sys.exit(1)
    return {
        "host": os.environ["POSTGRES_HOST"],
        "port": os.environ["POSTGRES_PORT"],
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
    }


def check_connection(config: dict[str, str], target: DbTarget) -> bool:
    try:
        conn = psycopg2.connect(host=config["host"], port=config["port"], user=config["user"], password=config["password"], dbname=target.dbname, connect_timeout=5)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
            logger.info("✅ %s ('%s') — connection OK", target.label, target.dbname)
            return True
        finally:
            conn.close()
    except psycopg2.OperationalError as exc:
        logger.error("❌ %s ('%s') — connection FAILED: %s", target.label, target.dbname, exc)
        return False


def main() -> None:
    config = load_config()
    targets = [
        DbTarget(label="Control-plane DB", dbname=os.getenv("POSTGRES_DB", "datapulse")),
        DbTarget(label="Source DB", dbname=os.getenv("POSTGRES_SOURCE_DB", "datapulse_source")),
    ]
    results = [check_connection(config, target) for target in targets]
    if all(results):
        logger.info("All database connections succeeded.")
        sys.exit(0)
    else:
        logger.error("One or more database connections failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
