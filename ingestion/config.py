from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class LoadStrategy(str, Enum):
    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"


@dataclass(frozen=True)
class TableIngestionSpec:
    table_name: str
    strategy: LoadStrategy
    watermark_column: str | None = None


INGESTION_REGISTRY: list[TableIngestionSpec] = [
    TableIngestionSpec("customers", LoadStrategy.FULL),
    TableIngestionSpec("products", LoadStrategy.FULL),
    TableIngestionSpec("orders", LoadStrategy.INCREMENTAL, watermark_column="created_at"),
    TableIngestionSpec("order_items", LoadStrategy.INCREMENTAL, watermark_column="created_at"),
    TableIngestionSpec("payments", LoadStrategy.INCREMENTAL, watermark_column="created_at"),
    TableIngestionSpec("subscriptions", LoadStrategy.FULL),
    TableIngestionSpec("events", LoadStrategy.INCREMENTAL, watermark_column="created_at"),
]


@dataclass(frozen=True)
class IngestionConfig:
    postgres_host: str
    postgres_port: str
    postgres_user: str
    postgres_password: str
    postgres_source_db: str
    s3_endpoint_url: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    s3_region: str
    api_base_url: str


def load_config() -> IngestionConfig:
    required = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_PASSWORD", "S3_ENDPOINT_URL", "S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_BUCKET"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")

    return IngestionConfig(
        postgres_host=os.environ["POSTGRES_HOST"],
        postgres_port=os.environ["POSTGRES_PORT"],
        postgres_user=os.environ["POSTGRES_USER"],
        postgres_password=os.environ["POSTGRES_PASSWORD"],
        postgres_source_db=os.getenv("POSTGRES_SOURCE_DB", "datapulse_source"),
        s3_endpoint_url=os.environ["S3_ENDPOINT_URL"],
        s3_access_key=os.environ["S3_ACCESS_KEY"],
        s3_secret_key=os.environ["S3_SECRET_KEY"],
        s3_bucket=os.environ["S3_BUCKET"],
        s3_region=os.getenv("S3_REGION", "us-east-1"),
        api_base_url=os.getenv("API_BASE_URL", "http://localhost:8000"),
    )
