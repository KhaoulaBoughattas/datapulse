from __future__ import annotations
import psycopg2
from streaming.config import StreamingConfig


def _connect(config: StreamingConfig):
    return psycopg2.connect(host=config.postgres_host, port=config.postgres_port, user=config.postgres_user, password=config.postgres_password, dbname=config.postgres_source_db)


def load_tenant_ids(config: StreamingConfig) -> list[str]:
    conn = _connect(config)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT tenant_id FROM tenants ORDER BY tenant_id;")
            return [r[0] for r in cur.fetchall()]
    finally:
        conn.close()


def load_customer_and_product_ids(config: StreamingConfig, tenant_id: str) -> tuple[list[int], list[int]]:
    conn = _connect(config)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT customer_id FROM customers WHERE tenant_id = %s;", (tenant_id,))
            customer_ids = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT product_id FROM products WHERE tenant_id = %s;", (tenant_id,))
            product_ids = [r[0] for r in cur.fetchall()]
        if not customer_ids or not product_ids:
            raise RuntimeError(f"No customers/products found for tenant '{tenant_id}'. Run scripts/generate_data.py first.")
        return customer_ids, product_ids
    finally:
        conn.close()
