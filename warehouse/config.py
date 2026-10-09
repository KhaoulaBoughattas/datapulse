"""Warehouse loader config. Auto-detects Snowflake vs. local Postgres
fallback based on whether real Snowflake credentials are present."""
from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class S3ReadConfig:
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str


@dataclass(frozen=True)
class PostgresWarehouseConfig:
    host: str
    port: str
    user: str
    password: str
    database: str


@dataclass(frozen=True)
class SnowflakeConfig:
    account: str
    user: str
    password: str
    role: str
    warehouse: str
    database: str


def load_s3_config() -> S3ReadConfig:
    required = ["S3_ENDPOINT_URL", "S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_BUCKET"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")
    return S3ReadConfig(endpoint_url=os.environ["S3_ENDPOINT_URL"], access_key=os.environ["S3_ACCESS_KEY"], secret_key=os.environ["S3_SECRET_KEY"], bucket=os.environ["S3_BUCKET"])


def load_postgres_warehouse_config() -> PostgresWarehouseConfig:
    required = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")
    return PostgresWarehouseConfig(host=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"], user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"], database=os.getenv("POSTGRES_WAREHOUSE_DB", "datapulse_warehouse"))


def load_snowflake_config() -> SnowflakeConfig:
    required = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError("Snowflake credentials not set. Set WAREHOUSE_BACKEND=postgres_local to use the local fallback instead.")
    return SnowflakeConfig(
        account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"], password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.getenv("SNOWFLAKE_ROLE", "DATAPULSE_TRANSFORMER"), warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "DATAPULSE_LOADING_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "DATAPULSE_RAW"),
    )


def resolve_backend() -> str:
    explicit = os.getenv("WAREHOUSE_BACKEND")
    if explicit:
        return explicit
    has_snowflake_creds = all(os.getenv(k) for k in ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"))
    return "snowflake" if has_snowflake_creds else "postgres_local"


TABLES: list[str] = ["customers", "products", "orders", "order_items", "payments", "subscriptions", "events"]
