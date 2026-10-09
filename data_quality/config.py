"""Table-level quality check configuration."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ForeignKeyCheck:
    child_column: str
    parent_table: str
    parent_column: str


@dataclass(frozen=True)
class TableQualityConfig:
    table_name: str
    expected_columns: set[str]
    not_null_columns: list[str] = field(default_factory=list)
    unique_columns: list[str] = field(default_factory=list)
    non_negative_columns: list[str] = field(default_factory=list)
    accepted_values: dict[str, list[str]] = field(default_factory=dict)
    foreign_keys: list[ForeignKeyCheck] = field(default_factory=list)
    future_timestamp_column: str | None = None


TABLE_CONFIGS: list[TableQualityConfig] = [
    TableQualityConfig("customers", {"customer_id", "tenant_id", "first_name", "last_name", "email", "country", "signup_date", "created_at"},
                       not_null_columns=["customer_id", "tenant_id", "email"], unique_columns=["customer_id"]),
    TableQualityConfig("products", {"product_id", "tenant_id", "name", "category", "price", "cost", "created_at"},
                       not_null_columns=["product_id"], unique_columns=["product_id"], non_negative_columns=["price", "cost"]),
    TableQualityConfig("orders", {"order_id", "tenant_id", "customer_id", "order_date", "status", "total_amount", "created_at"},
                       not_null_columns=["order_id", "customer_id"], unique_columns=["order_id"], non_negative_columns=["total_amount"],
                       accepted_values={"status": ["completed", "pending", "cancelled", "refunded"]},
                       foreign_keys=[ForeignKeyCheck("customer_id", "customers", "customer_id")]),
    TableQualityConfig("order_items", {"order_item_id", "tenant_id", "order_id", "product_id", "quantity", "unit_price", "created_at"},
                       not_null_columns=["order_item_id", "order_id", "product_id"], unique_columns=["order_item_id"], non_negative_columns=["unit_price"],
                       foreign_keys=[ForeignKeyCheck("order_id", "orders", "order_id"), ForeignKeyCheck("product_id", "products", "product_id")]),
    TableQualityConfig("payments", {"payment_id", "tenant_id", "order_id", "amount", "payment_method", "status", "paid_at", "created_at"},
                       not_null_columns=["payment_id", "order_id"], unique_columns=["payment_id"], non_negative_columns=["amount"],
                       accepted_values={"status": ["success", "pending", "failed", "refunded"]},
                       foreign_keys=[ForeignKeyCheck("order_id", "orders", "order_id")]),
    TableQualityConfig("subscriptions", {"subscription_id", "tenant_id", "customer_id", "plan", "status", "mrr_amount", "started_at", "cancelled_at", "created_at"},
                       not_null_columns=["subscription_id", "customer_id"], unique_columns=["subscription_id"], non_negative_columns=["mrr_amount"],
                       accepted_values={"plan": ["basic", "pro", "enterprise"]},
                       foreign_keys=[ForeignKeyCheck("customer_id", "customers", "customer_id")]),
    TableQualityConfig("events", {"event_id", "tenant_id", "customer_id", "session_id", "event_type", "product_id", "event_timestamp", "created_at"},
                       not_null_columns=["event_id"], unique_columns=["event_id"],
                       accepted_values={"event_type": ["product_view", "add_to_cart", "checkout", "purchase", "login", "subscription_created", "subscription_cancelled"]},
                       foreign_keys=[ForeignKeyCheck("customer_id", "customers", "customer_id"), ForeignKeyCheck("product_id", "products", "product_id")],
                       future_timestamp_column="event_timestamp"),
]
