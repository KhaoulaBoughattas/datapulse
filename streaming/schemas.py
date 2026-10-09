"""Clickstream event schema — schema_version included from day one."""
from __future__ import annotations
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from streaming.config import SCHEMA_VERSION


@dataclass(frozen=True)
class ClickstreamEvent:
    event_id: str
    schema_version: int
    tenant_id: str
    session_id: str
    event_type: str
    event_timestamp: str
    produced_at: str
    customer_id: int | None = None
    product_id: int | None = None
    amount: float | None = None
    device_type: str | None = None
    correlates_with_event_id: str | None = None

    def to_json_bytes(self) -> bytes:
        return json.dumps(asdict(self)).encode("utf-8")

    def partition_key(self) -> str:
        return str(self.customer_id) if self.customer_id is not None else self.session_id


def new_event_id() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_event(tenant_id, session_id, event_type, customer_id, product_id=None, amount=None, device_type=None, correlates_with_event_id=None) -> ClickstreamEvent:
    ts = now_iso()
    return ClickstreamEvent(
        event_id=new_event_id(), schema_version=SCHEMA_VERSION, tenant_id=tenant_id, session_id=session_id,
        event_type=event_type, event_timestamp=ts, produced_at=ts, customer_id=customer_id, product_id=product_id,
        amount=amount, device_type=device_type, correlates_with_event_id=correlates_with_event_id,
    )
