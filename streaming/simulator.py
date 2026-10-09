"""Generates realistic clickstream events referencing real customer/product ids."""
from __future__ import annotations
import logging
import random
import uuid
from confluent_kafka import Producer
from streaming.config import (
    BROWSING_EVENT_TYPES, BROWSING_EVENT_WEIGHTS, DEVICE_TYPES, ORDER_EVENT_TYPES, ORDER_EVENT_WEIGHTS,
    PAYMENT_CORRELATION_RATE, PAYMENT_EVENT_TYPES, PAYMENT_EVENT_WEIGHTS, PRODUCT_LINKED_EVENT_TYPES, TOPIC_BY_EVENT_TYPE,
)
from streaming.producer import send_event
from streaming.schemas import ClickstreamEvent, build_event

logger = logging.getLogger("streaming.simulator")


class EventSimulator:
    def __init__(self, tenant_id, customer_ids, product_ids, rng: random.Random) -> None:
        self.tenant_id = tenant_id
        self.customer_ids = customer_ids
        self.product_ids = product_ids
        self.rng = rng
        self._session_pool = [str(uuid.uuid4()) for _ in range(max(10, len(customer_ids) // 20))]

    def _pick_customer(self) -> int | None:
        return self.rng.choice(self.customer_ids) if self.rng.random() > 0.20 else None

    def generate_next(self) -> list[tuple[str, ClickstreamEvent]]:
        session_id = self.rng.choice(self._session_pool)
        customer_id = self._pick_customer()
        device_type = self.rng.choice(DEVICE_TYPES)

        if self.rng.random() < 0.75:
            event_type = self.rng.choices(BROWSING_EVENT_TYPES, weights=BROWSING_EVENT_WEIGHTS, k=1)[0]
        else:
            event_type = self.rng.choices(ORDER_EVENT_TYPES, weights=ORDER_EVENT_WEIGHTS, k=1)[0]

        product_id = self.rng.choice(self.product_ids) if event_type in PRODUCT_LINKED_EVENT_TYPES else None
        amount = round(self.rng.uniform(10, 500), 2) if event_type == "purchase" else None

        primary_event = build_event(tenant_id=self.tenant_id, session_id=session_id, event_type=event_type, customer_id=customer_id, product_id=product_id, amount=amount, device_type=device_type)
        results = [(TOPIC_BY_EVENT_TYPE[event_type], primary_event)]

        if event_type == "purchase" and self.rng.random() < PAYMENT_CORRELATION_RATE:
            payment_type = self.rng.choices(PAYMENT_EVENT_TYPES, weights=PAYMENT_EVENT_WEIGHTS, k=1)[0]
            payment_event = build_event(tenant_id=self.tenant_id, session_id=session_id, event_type=payment_type, customer_id=customer_id, amount=amount, device_type=device_type, correlates_with_event_id=primary_event.event_id)
            results.append((TOPIC_BY_EVENT_TYPE[payment_type], payment_event))
        return results

    def run(self, producer: Producer, count: int) -> dict[str, int]:
        topic_counts: dict[str, int] = {}
        for _ in range(count):
            for topic, event in self.generate_next():
                send_event(producer, topic, event)
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        producer.flush(timeout=10)
        return topic_counts
