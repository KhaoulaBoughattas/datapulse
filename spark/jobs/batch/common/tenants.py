from __future__ import annotations
import os
import psycopg2


def list_tenant_ids() -> list[str]:
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.getenv("POSTGRES_SOURCE_DB", "datapulse_source"),
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT tenant_id FROM tenants ORDER BY tenant_id;")
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()
