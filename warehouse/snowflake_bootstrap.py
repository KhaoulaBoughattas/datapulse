#!/usr/bin/env python
"""One-time Snowflake bootstrap: creates warehouses, roles, databases,
schemas, and grants. Requires ACCOUNTADMIN. Skip this entirely if you
don't have a Snowflake account — the local Postgres fallback is default."""
from __future__ import annotations
import logging
import os
from pathlib import Path
import snowflake.connector
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("warehouse.snowflake_bootstrap")
SQL_DIR = Path(__file__).resolve().parents[1] / "infrastructure" / "snowflake" / "sql"


def main() -> None:
    load_dotenv()
    required = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise SystemExit(f"Missing {missing}. Skip this step if using the local Postgres fallback (default).")

    conn = snowflake.connector.connect(account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"], password=os.environ["SNOWFLAKE_PASSWORD"], role=os.getenv("SNOWFLAKE_BOOTSTRAP_ROLE", "ACCOUNTADMIN"))
    try:
        for sql_file in sorted(SQL_DIR.glob("*.sql")):
            logger.info("Running %s...", sql_file.name)
            statements = sql_file.read_text(encoding="utf-8")
            with conn.cursor() as cur:
                for statement in statements.split(";"):
                    statement = statement.strip()
                    if statement and not statement.startswith("--"):
                        cur.execute(statement)
    finally:
        conn.close()
    logger.info("Snowflake bootstrap complete.")


if __name__ == "__main__":
    main()
