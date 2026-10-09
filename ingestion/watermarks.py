from __future__ import annotations

import logging
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.engine import Connection

logger = logging.getLogger("ingestion.watermarks")
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def get_watermark(conn: Connection, tenant_id: str, table_name: str) -> datetime:
    row = conn.execute(
        text("SELECT last_extracted_at FROM ingestion_watermarks WHERE tenant_id = :tenant_id AND table_name = :table_name"),
        {"tenant_id": tenant_id, "table_name": table_name},
    ).fetchone()
    return row[0] if row else EPOCH


def set_watermark(conn: Connection, tenant_id: str, table_name: str, watermark: datetime) -> None:
    conn.execute(
        text(
            "INSERT INTO ingestion_watermarks (tenant_id, table_name, last_extracted_at, updated_at) "
            "VALUES (:tenant_id, :table_name, :watermark, now()) "
            "ON CONFLICT (tenant_id, table_name) DO UPDATE SET last_extracted_at = :watermark, updated_at = now()"
        ),
        {"tenant_id": tenant_id, "table_name": table_name, "watermark": watermark},
    )
