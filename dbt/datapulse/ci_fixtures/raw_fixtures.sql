-- Minimal RAW fixture for CI's dbt-tests job.
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE raw.tenants (tenant_id TEXT, name TEXT);
INSERT INTO raw.tenants VALUES ('acme', 'ACME Corporation');

CREATE TABLE raw.customers (customer_id BIGINT, tenant_id TEXT, first_name TEXT, last_name TEXT, email TEXT, country TEXT, signup_date DATE, created_at TIMESTAMP);
INSERT INTO raw.customers VALUES
    (1, 'acme', 'Alice', 'Smith', 'alice@example.com', 'United States', '2026-01-01', '2026-01-01 00:00:00'),
    (2, 'acme', 'Bob', 'Jones', 'bob@example.com', 'United Kingdom', '2026-01-05', '2026-01-05 00:00:00');

CREATE TABLE raw.products (product_id BIGINT, tenant_id TEXT, name TEXT, category TEXT, price DOUBLE PRECISION, cost DOUBLE PRECISION, created_at TIMESTAMP);
INSERT INTO raw.products VALUES
    (1, 'acme', 'Widget', 'Electronics', 19.99, 8.50, '2026-01-01 00:00:00'),
    (2, 'acme', 'Gadget', 'Electronics', 49.99, 20.00, '2026-01-01 00:00:00');

CREATE TABLE raw.orders (order_id BIGINT, tenant_id TEXT, customer_id BIGINT, order_date TIMESTAMP, status TEXT, total_amount DOUBLE PRECISION, created_at TIMESTAMP);
INSERT INTO raw.orders VALUES
    (1, 'acme', 1, '2026-02-01 10:00:00', 'completed', 19.99, '2026-02-01 10:00:00'),
    (2, 'acme', 2, '2026-02-02 11:00:00', 'completed', 49.99, '2026-02-02 11:00:00');

CREATE TABLE raw.order_items (order_item_id BIGINT, tenant_id TEXT, order_id BIGINT, product_id BIGINT, quantity INT, unit_price DOUBLE PRECISION, created_at TIMESTAMP);
INSERT INTO raw.order_items VALUES
    (1, 'acme', 1, 1, 1, 19.99, '2026-02-01 10:00:00'),
    (2, 'acme', 2, 2, 1, 49.99, '2026-02-02 11:00:00');

CREATE TABLE raw.payments (payment_id BIGINT, tenant_id TEXT, order_id BIGINT, amount DOUBLE PRECISION, payment_method TEXT, status TEXT, paid_at TIMESTAMP, created_at TIMESTAMP);
INSERT INTO raw.payments VALUES
    (1, 'acme', 1, 19.99, 'credit_card', 'success', '2026-02-01 10:05:00', '2026-02-01 10:05:00'),
    (2, 'acme', 2, 49.99, 'paypal', 'success', '2026-02-02 11:05:00', '2026-02-02 11:05:00');

CREATE TABLE raw.subscriptions (subscription_id BIGINT, tenant_id TEXT, customer_id BIGINT, plan TEXT, status TEXT, mrr_amount DOUBLE PRECISION, started_at TIMESTAMP, cancelled_at TIMESTAMP, created_at TIMESTAMP);
INSERT INTO raw.subscriptions VALUES
    (1, 'acme', 1, 'pro', 'active', 29.99, '2026-01-01 00:00:00', NULL, '2026-01-01 00:00:00');

CREATE TABLE raw.events (event_id TEXT, tenant_id TEXT, customer_id BIGINT, session_id TEXT, event_type TEXT, product_id BIGINT, event_timestamp TIMESTAMP, created_at TIMESTAMP);
INSERT INTO raw.events VALUES
    ('evt-1', 'acme', 1, 'sess-1', 'login', NULL, '2026-02-01 09:55:00', '2026-02-01 09:55:00'),
    ('evt-2', 'acme', 1, 'sess-1', 'purchase', 1, '2026-02-01 10:00:00', '2026-02-01 10:00:00');
