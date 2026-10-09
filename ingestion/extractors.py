from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ingestion.config import IngestionConfig, LoadStrategy, TableIngestionSpec
from ingestion.watermarks import get_watermark

logger = logging.getLogger("ingestion.extractors")


def get_source_engine(config: IngestionConfig) -> Engine:
    url = f"postgresql+psycopg2://{config.postgres_user}:{config.postgres_password}@{config.postgres_host}:{config.postgres_port}/{config.postgres_source_db}"
    return create_engine(url)


@dataclass
class ExtractionResult:
    dataframe: pd.DataFrame
    new_watermark: datetime | None
    row_count: int


def extract_table(engine: Engine, tenant_id: str, spec: TableIngestionSpec) -> ExtractionResult:
    with engine.connect() as conn:
        if spec.strategy == LoadStrategy.FULL:
            df = pd.read_sql(text(f"SELECT * FROM {spec.table_name} WHERE tenant_id = :tenant_id"), conn, params={"tenant_id": tenant_id})
            logger.info("[%s] FULL load of '%s': %d rows", tenant_id, spec.table_name, len(df))
            return ExtractionResult(dataframe=df, new_watermark=None, row_count=len(df))

        watermark = get_watermark(conn, tenant_id, spec.table_name)
        df = pd.read_sql(
            text(f"SELECT * FROM {spec.table_name} WHERE tenant_id = :tenant_id AND {spec.watermark_column} > :watermark ORDER BY {spec.watermark_column} ASC"),
            conn, params={"tenant_id": tenant_id, "watermark": watermark},
        )
        logger.info("[%s] INCREMENTAL load of '%s' since %s: %d new rows", tenant_id, spec.table_name, watermark.isoformat(), len(df))

        if len(df) == 0:
            return ExtractionResult(dataframe=df, new_watermark=watermark, row_count=0)

        observed_max = pd.to_datetime(df[spec.watermark_column]).max()
        new_watermark = observed_max.to_pydatetime()
        if new_watermark.tzinfo is None:
            new_watermark = new_watermark.replace(tzinfo=timezone.utc)

        return ExtractionResult(dataframe=df, new_watermark=new_watermark, row_count=len(df))


def commit_watermark(engine: Engine, tenant_id: str, table_name: str, new_watermark: datetime) -> None:
    from ingestion.watermarks import set_watermark
    with engine.begin() as conn:
        set_watermark(conn, tenant_id, table_name, new_watermark)
