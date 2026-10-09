"""Loads a DataFrame into Snowflake's RAW database via PUT + COPY INTO
a table (internal) stage. RAW is deliberately schema-light (VARIANT)."""
from __future__ import annotations
import logging
import tempfile
from pathlib import Path
import pandas as pd
import snowflake.connector
from warehouse.config import SnowflakeConfig

logger = logging.getLogger("warehouse.snowflake_loader")

_RAW_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS RAW.{table} (
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _raw_data VARIANT
);
"""


def get_connection(config: SnowflakeConfig):
    return snowflake.connector.connect(account=config.account, user=config.user, password=config.password, role=config.role, warehouse=config.warehouse, database=config.database, schema="RAW")


def load_table(conn, table_name: str, df: pd.DataFrame) -> int:
    table = table_name.upper()
    with conn.cursor() as cur:
        cur.execute(_RAW_TABLE_DDL.format(table=table))
        cur.execute(f"TRUNCATE TABLE IF EXISTS RAW.{table}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        json_path = Path(tmp_dir) / f"{table_name}.json"
        df.to_json(json_path, orient="records", lines=True, date_format="iso")
        with conn.cursor() as cur:
            cur.execute(f"PUT file://{json_path} @%{table} OVERWRITE = TRUE AUTO_COMPRESS = TRUE")
            cur.execute(f"""
                COPY INTO RAW.{table} (_raw_data) FROM @%{table}
                FILE_FORMAT = (TYPE = JSON STRIP_OUTER_ARRAY = FALSE)
                ON_ERROR = ABORT_STATEMENT PURGE = TRUE
            """)
    logger.info("Loaded %d rows into RAW.%s (Snowflake)", len(df), table)
    return len(df)
