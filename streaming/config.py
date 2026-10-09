"""Streaming configuration: Kafka topics, event-type reference data."""
from __future__ import annotations
import os
from dataclasses import dataclass

TOPIC_USER_EVENTS = "user-events"
TOPIC_ORDER_EVENTS = "order-events"
TOPIC_PAYMENT_EVENTS = "payment-events"

TOPIC_PARTITIONS: dict[str, int] = {TOPIC_USER_EVENTS: 6, TOPIC_ORDER_EVENTS: 3, TOPIC_PAYMENT_EVENTS: 3}
TOPIC_REPLICATION_FACTOR = 1
TOPIC_RETENTION_MS = 7 * 24 * 60 * 60 * 1000

BROWSING_EVENT_TYPES = ["product_view", "add_to_cart", "login", "subscription_created", "subscription_cancelled"]
BROWSING_EVENT_WEIGHTS = [0.55, 0.25, 0.13, 0.04, 0.03]
ORDER_EVENT_TYPES = ["checkout", "purchase"]
ORDER_EVENT_WEIGHTS = [0.6, 0.4]
PAYMENT_EVENT_TYPES = ["payment_succeeded", "payment_failed"]
PAYMENT_EVENT_WEIGHTS = [0.92, 0.08]
PAYMENT_CORRELATION_RATE = 0.85
PRODUCT_LINKED_EVENT_TYPES = {"product_view", "add_to_cart", "checkout", "purchase"}
DEVICE_TYPES = ["desktop", "mobile", "tablet"]

TOPIC_BY_EVENT_TYPE: dict[str, str] = {
    **{et: TOPIC_USER_EVENTS for et in BROWSING_EVENT_TYPES},
    **{et: TOPIC_ORDER_EVENTS for et in ORDER_EVENT_TYPES},
    **{et: TOPIC_PAYMENT_EVENTS for et in PAYMENT_EVENT_TYPES},
}
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class StreamingConfig:
    bootstrap_servers: str
    postgres_host: str
    postgres_port: str
    postgres_user: str
    postgres_password: str
    postgres_source_db: str


def load_config() -> StreamingConfig:
    required = ["KAFKA_BOOTSTRAP_SERVERS", "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")
    return StreamingConfig(
        bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"],
        postgres_host=os.environ["POSTGRES_HOST"], postgres_port=os.environ["POSTGRES_PORT"],
        postgres_user=os.environ["POSTGRES_USER"], postgres_password=os.environ["POSTGRES_PASSWORD"],
        postgres_source_db=os.getenv("POSTGRES_SOURCE_DB", "datapulse_source"),
    )
