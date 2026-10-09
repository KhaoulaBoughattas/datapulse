"""Loads a DataFrame into the local Postgres RAW schema — the fallback
warehouse used whenever Snowflake credentials aren't configured."""
from __future__ import annotations
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from warehouse.config import PostgresWarehouseConfig

logger = logging.getLogger("warehouse.postgres_loader")


def get_warehouse_engine(config: PostgresWarehouseConfig) -> Engine:
    url = f"postgresql+psycopg2://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}"
    return create_engine(url)


def load_table(engine: Engine, table_name: str, df: pd.DataFrame) -> int:
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
    df.to_sql(table_name, engine, schema="raw", if_exists="replace", index=False, method="multi", chunksize=5000)
    logger.info("Loaded %d rows into raw.%s (local Postgres warehouse)", len(df), table_name)
    return len(df)
