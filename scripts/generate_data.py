#!/usr/bin/env python
"""
DataPulse synthetic data generator.

Usage:
    python scripts/generate_data.py --customers 10000 --orders 50000
    python scripts/generate_data.py --seed 42 --reset
"""
from __future__ import annotations

import logging
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv  # noqa: E402
from faker import Faker  # noqa: E402

from data_generator import db, generators  # noqa: E402
from data_generator.config import GeneratorConfig, parse_args  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("generate_data")


def run(config: GeneratorConfig) -> None:
    load_dotenv()
    fake = Faker()
    if config.seed is not None:
        fake.seed_instance(config.seed)

    conn = db.get_connection()
    try:
        if config.reset:
            db.reset_schema(conn)
        db.apply_schema(conn)

        generators.generate_tenants(conn, config.tenants)

        totals = {"customers": 0, "products": 0, "orders": 0, "order_items": 0, "payments": 0, "subscriptions": 0, "events": 0}

        customers_per_tenant = config.customers_per_tenant()
        products_per_tenant = config.products_per_tenant()
        orders_per_tenant = config.orders_per_tenant()
        events_per_tenant = config.events_per_tenant()

        for idx, tenant_id in enumerate(config.tenants):
            rng_seed = None if config.seed is None else config.seed + idx
            rng = random.Random(rng_seed)

            customer_ids = generators.generate_customers(conn, tenant_id, customers_per_tenant[idx], rng, fake, config.batch_size)
            totals["customers"] += len(customer_ids)

            product_catalog = generators.generate_products(conn, tenant_id, products_per_tenant[idx], rng, fake, config.batch_size)
            totals["products"] += len(product_catalog)

            batch_counts = generators.generate_orders_items_payments(
                conn, tenant_id, customer_ids, product_catalog, orders_per_tenant[idx], config.order_items_max, config.batch_size, rng
            )
            totals["orders"] += batch_counts["orders"]
            totals["order_items"] += batch_counts["order_items"]
            totals["payments"] += batch_counts["payments"]

            n_subscriptions = generators.generate_subscriptions(conn, tenant_id, customer_ids, config.subscription_rate, rng)
            totals["subscriptions"] += n_subscriptions

            product_ids = [pid for pid, _ in product_catalog]
            n_events = generators.generate_events(conn, tenant_id, customer_ids, product_ids, events_per_tenant[idx], config.batch_size, rng, fake)
            totals["events"] += n_events

            logger.info("[%s] done", tenant_id)

        logger.info("=" * 60)
        logger.info("GENERATION COMPLETE")
        for entity, count in totals.items():
            logger.info("  %-15s %10s rows", entity, f"{count:,}")
        logger.info("=" * 60)
    finally:
        conn.close()


def main() -> None:
    config = parse_args()
    run(config)


if __name__ == "__main__":
    main()
