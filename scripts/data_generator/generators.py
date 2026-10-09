from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime, timedelta, timezone

from faker import Faker
from psycopg2.extensions import connection as PGConnection
from psycopg2.extras import Json, execute_values

from data_generator.reference_data import (
    COUNTRIES, COUNTRY_WEIGHTS, DEVICE_TYPES, EVENT_TYPE_WEIGHTS, EVENT_TYPES,
    ORDER_STATUS_WEIGHTS, ORDER_STATUSES, PAYMENT_METHODS, PRODUCT_CATEGORIES,
    PRODUCT_LINKED_EVENT_TYPES, SUBSCRIPTION_PLANS, SUBSCRIPTION_STATUS_WEIGHTS,
    TENANT_DISPLAY_NAMES,
)

logger = logging.getLogger("data_generator.generators")
_UTC_NOW = datetime.now(timezone.utc)


def generate_tenants(conn: PGConnection, tenant_slugs: list[str]) -> None:
    rows = [(slug, TENANT_DISPLAY_NAMES.get(slug, slug.title())) for slug in tenant_slugs]
    with conn.cursor() as cur:
        execute_values(cur, "INSERT INTO tenants (tenant_id, name) VALUES %s ON CONFLICT (tenant_id) DO NOTHING;", rows)
    conn.commit()
    logger.info("Ensured %d tenant(s) exist: %s", len(tenant_slugs), ", ".join(tenant_slugs))


def generate_customers(conn, tenant_id, count, rng, fake, batch_size):
    customer_ids = []
    for size in _batch_sizes(count, batch_size):
        rows = []
        for _ in range(size):
            first_name = fake.first_name()
            last_name = fake.last_name()
            domain = fake.free_email_domain()
            email = f"{first_name.lower()}.{last_name.lower()}{rng.randint(100, 9999)}@{domain}"
            country = rng.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0]
            signup_date = (_UTC_NOW - timedelta(days=rng.randint(0, 730))).date()
            rows.append((tenant_id, first_name, last_name, email, country, signup_date))
        with conn.cursor() as cur:
            returned = execute_values(
                cur, "INSERT INTO customers (tenant_id, first_name, last_name, email, country, signup_date) VALUES %s RETURNING customer_id;",
                rows, fetch=True,
            )
        customer_ids.extend(r[0] for r in returned)
        conn.commit()
    return customer_ids


def generate_products(conn, tenant_id, count, rng, fake, batch_size):
    catalog = []
    for size in _batch_sizes(count, batch_size):
        rows, prices = [], []
        for _ in range(size):
            category = rng.choice(list(PRODUCT_CATEGORIES.keys()))
            min_price, max_price = PRODUCT_CATEGORIES[category]
            price = round(rng.uniform(min_price, max_price), 2)
            cost = round(price * rng.uniform(0.4, 0.7), 2)
            name = fake.catch_phrase()
            rows.append((tenant_id, name, category, price, cost))
            prices.append(price)
        with conn.cursor() as cur:
            returned = execute_values(cur, "INSERT INTO products (tenant_id, name, category, price, cost) VALUES %s RETURNING product_id;", rows, fetch=True)
        catalog.extend((r[0], p) for r, p in zip(returned, prices, strict=True))
        conn.commit()
    return catalog


def generate_orders_items_payments(conn, tenant_id, customer_ids, product_catalog, count, order_items_max, batch_size, rng):
    counts = {"orders": 0, "order_items": 0, "payments": 0}
    for size in _batch_sizes(count, batch_size):
        order_specs, item_specs = [], []
        for _ in range(size):
            customer_id = rng.choice(customer_ids)
            order_date = _UTC_NOW - timedelta(days=rng.randint(0, 180), seconds=rng.randint(0, 86400))
            status = rng.choices(["completed", "pending", "cancelled", "refunded"], weights=ORDER_STATUS_WEIGHTS, k=1)[0]
            n_items = rng.randint(1, order_items_max)
            items = []
            for _ in range(n_items):
                product_id, unit_price = rng.choice(product_catalog)
                quantity = rng.randint(1, 3)
                items.append((product_id, quantity, unit_price))
            total_amount = round(sum(qty * price for _, qty, price in items), 2)
            order_specs.append((customer_id, order_date, status, total_amount))
            item_specs.append(items)

        order_rows = [(tenant_id, c, d, s, t) for c, d, s, t in order_specs]
        with conn.cursor() as cur:
            returned_order_ids = execute_values(cur, "INSERT INTO orders (tenant_id, customer_id, order_date, status, total_amount) VALUES %s RETURNING order_id;", order_rows, fetch=True)
        order_ids = [r[0] for r in returned_order_ids]

        item_rows = []
        for order_id, items in zip(order_ids, item_specs, strict=True):
            for product_id, quantity, unit_price in items:
                item_rows.append((tenant_id, order_id, product_id, quantity, unit_price))
        with conn.cursor() as cur:
            execute_values(cur, "INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price) VALUES %s;", item_rows)

        payment_rows = []
        for order_id, (_, order_date, status, total_amount) in zip(order_ids, order_specs, strict=True):
            payment_method = rng.choice(PAYMENT_METHODS)
            if status == "completed":
                payment_status, paid_at = "success", order_date + timedelta(minutes=rng.randint(1, 30))
            elif status == "refunded":
                payment_status, paid_at = "refunded", order_date + timedelta(minutes=rng.randint(1, 30))
            elif status == "cancelled":
                payment_status, paid_at = "failed", None
            else:
                payment_status, paid_at = "pending", None
            payment_rows.append((tenant_id, order_id, total_amount, payment_method, payment_status, paid_at))
        with conn.cursor() as cur:
            execute_values(cur, "INSERT INTO payments (tenant_id, order_id, amount, payment_method, status, paid_at) VALUES %s;", payment_rows)

        conn.commit()
        counts["orders"] += len(order_rows)
        counts["order_items"] += len(item_rows)
        counts["payments"] += len(payment_rows)
    return counts


def generate_subscriptions(conn, tenant_id, customer_ids, rate, rng):
    sample_size = int(len(customer_ids) * rate)
    subscribed = rng.sample(customer_ids, k=min(sample_size, len(customer_ids)))
    rows = []
    for customer_id in subscribed:
        plan = rng.choice(list(SUBSCRIPTION_PLANS.keys()))
        mrr = SUBSCRIPTION_PLANS[plan]
        status = rng.choices(list(SUBSCRIPTION_STATUS_WEIGHTS.keys()), weights=list(SUBSCRIPTION_STATUS_WEIGHTS.values()), k=1)[0]
        started_at = _UTC_NOW - timedelta(days=rng.randint(10, 600))
        cancelled_at = started_at + timedelta(days=rng.randint(5, 300)) if status == "cancelled" else None
        rows.append((tenant_id, customer_id, plan, status, mrr, started_at, cancelled_at))
    if rows:
        with conn.cursor() as cur:
            execute_values(cur, "INSERT INTO subscriptions (tenant_id, customer_id, plan, status, mrr_amount, started_at, cancelled_at) VALUES %s;", rows)
        conn.commit()
    return len(rows)


def generate_events(conn, tenant_id, customer_ids, product_ids, count, batch_size, rng, fake):
    session_pool = [str(uuid.uuid4()) for _ in range(max(1, count // 4))]
    total = 0
    for size in _batch_sizes(count, batch_size):
        rows = []
        for _ in range(size):
            event_type = rng.choices(EVENT_TYPES, weights=EVENT_TYPE_WEIGHTS, k=1)[0]
            customer_id = rng.choice(customer_ids) if rng.random() > 0.20 else None
            product_id = rng.choice(product_ids) if event_type in PRODUCT_LINKED_EVENT_TYPES else None
            event_timestamp = _UTC_NOW - timedelta(seconds=rng.randint(0, 30 * 86400))
            payload = Json({"device_type": rng.choice(DEVICE_TYPES), "referrer": fake.domain_name()})
            rows.append((str(uuid.uuid4()), tenant_id, customer_id, rng.choice(session_pool), event_type, product_id, event_timestamp, payload))
        with conn.cursor() as cur:
            execute_values(cur, "INSERT INTO events (event_id, tenant_id, customer_id, session_id, event_type, product_id, event_timestamp, payload) VALUES %s;", rows)
        conn.commit()
        total += len(rows)
    return total


def _batch_sizes(total: int, batch_size: int) -> list[int]:
    full_batches, remainder = divmod(total, batch_size)
    sizes = [batch_size] * full_batches
    if remainder:
        sizes.append(remainder)
    return sizes
