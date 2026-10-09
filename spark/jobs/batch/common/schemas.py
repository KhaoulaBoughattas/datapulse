"""Explicit canonical schemas for every bronze table — the enforcement
boundary between bronze and silver. See docs/spark.md for the dedup
tie-breaker distinction (FULL vs INCREMENTAL load strategy tables)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pyspark.sql.types import DateType, DoubleType, IntegerType, LongType, StringType, TimestampType


class LoadStrategy(str, Enum):
    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    dtype: object


@dataclass(frozen=True)
class SilverTableSpec:
    table_name: str
    primary_key: str
    strategy: LoadStrategy
    columns: list[ColumnSpec]
    derived_partition_column: str | None = None
    derive_from_column: str | None = None

    @property
    def dedup_order_column(self) -> str:
        return "ingestion_date" if self.strategy == LoadStrategy.FULL else "created_at"


SILVER_TABLE_SPECS: list[SilverTableSpec] = [
    SilverTableSpec("customers", "customer_id", LoadStrategy.FULL, [
        ColumnSpec("customer_id", LongType()), ColumnSpec("tenant_id", StringType()),
        ColumnSpec("first_name", StringType()), ColumnSpec("last_name", StringType()),
        ColumnSpec("email", StringType()), ColumnSpec("country", StringType()),
        ColumnSpec("signup_date", DateType()), ColumnSpec("created_at", TimestampType()),
    ]),
    SilverTableSpec("products", "product_id", LoadStrategy.FULL, [
        ColumnSpec("product_id", LongType()), ColumnSpec("tenant_id", StringType()),
        ColumnSpec("name", StringType()), ColumnSpec("category", StringType()),
        ColumnSpec("price", DoubleType()), ColumnSpec("cost", DoubleType()),
        ColumnSpec("created_at", TimestampType()),
    ]),
    SilverTableSpec("orders", "order_id", LoadStrategy.INCREMENTAL, [
        ColumnSpec("order_id", LongType()), ColumnSpec("tenant_id", StringType()),
        ColumnSpec("customer_id", LongType()), ColumnSpec("order_date", TimestampType()),
        ColumnSpec("status", StringType()), ColumnSpec("total_amount", DoubleType()),
        ColumnSpec("created_at", TimestampType()),
    ], derived_partition_column="order_month", derive_from_column="order_date"),
    SilverTableSpec("order_items", "order_item_id", LoadStrategy.INCREMENTAL, [
        ColumnSpec("order_item_id", LongType()), ColumnSpec("tenant_id", StringType()),
        ColumnSpec("order_id", LongType()), ColumnSpec("product_id", LongType()),
        ColumnSpec("quantity", IntegerType()), ColumnSpec("unit_price", DoubleType()),
        ColumnSpec("created_at", TimestampType()),
    ]),
    SilverTableSpec("payments", "payment_id", LoadStrategy.INCREMENTAL, [
        ColumnSpec("payment_id", LongType()), ColumnSpec("tenant_id", StringType()),
        ColumnSpec("order_id", LongType()), ColumnSpec("amount", DoubleType()),
        ColumnSpec("payment_method", StringType()), ColumnSpec("status", StringType()),
        ColumnSpec("paid_at", TimestampType()), ColumnSpec("created_at", TimestampType()),
    ]),
    SilverTableSpec("subscriptions", "subscription_id", LoadStrategy.FULL, [
        ColumnSpec("subscription_id", LongType()), ColumnSpec("tenant_id", StringType()),
        ColumnSpec("customer_id", LongType()), ColumnSpec("plan", StringType()),
        ColumnSpec("status", StringType()), ColumnSpec("mrr_amount", DoubleType()),
        ColumnSpec("started_at", TimestampType()), ColumnSpec("cancelled_at", TimestampType()),
        ColumnSpec("created_at", TimestampType()),
    ]),
    SilverTableSpec("events", "event_id", LoadStrategy.INCREMENTAL, [
        ColumnSpec("event_id", StringType()), ColumnSpec("tenant_id", StringType()),
        ColumnSpec("customer_id", LongType()), ColumnSpec("session_id", StringType()),
        ColumnSpec("event_type", StringType()), ColumnSpec("product_id", LongType()),
        ColumnSpec("event_timestamp", TimestampType()), ColumnSpec("created_at", TimestampType()),
    ], derived_partition_column="event_month", derive_from_column="event_timestamp"),
]
