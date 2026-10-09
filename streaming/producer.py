"""Kafka producer wrapper, idempotent. See docs/kafka.md for exactly
what enable.idempotence does and doesn't guarantee."""
from __future__ import annotations
import logging
from confluent_kafka import Producer
from streaming.config import StreamingConfig
from streaming.schemas import ClickstreamEvent

logger = logging.getLogger("streaming.producer")


def build_producer(config: StreamingConfig) -> Producer:
    return Producer({
        "bootstrap.servers": config.bootstrap_servers,
        "enable.idempotence": True,
        "acks": "all",
        "linger.ms": 20,
        "compression.type": "snappy",
        "client.id": "datapulse-event-simulator",
    })


def _delivery_callback(err, msg) -> None:
    if err is not None:
        logger.error("Delivery failed for key=%s: %s", msg.key(), err)


def send_event(producer: Producer, topic: str, event: ClickstreamEvent) -> None:
    producer.produce(topic=topic, key=event.partition_key().encode("utf-8"), value=event.to_json_bytes(), callback=_delivery_callback)
    producer.poll(0)
