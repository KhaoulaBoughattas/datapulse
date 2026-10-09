CREATE TABLE IF NOT EXISTS tenants (
    tenant_id   TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id   BIGSERIAL PRIMARY KEY,
    tenant_id     TEXT NOT NULL REFERENCES tenants (tenant_id),
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    email         TEXT NOT NULL,
    country       TEXT NOT NULL,
    signup_date   DATE NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_customers_tenant ON customers (tenant_id);

CREATE TABLE IF NOT EXISTS products (
    product_id    BIGSERIAL PRIMARY KEY,
    tenant_id     TEXT NOT NULL REFERENCES tenants (tenant_id),
    name          TEXT NOT NULL,
    category      TEXT NOT NULL,
    price         NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    cost          NUMERIC(10, 2) NOT NULL CHECK (cost >= 0),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_products_tenant ON products (tenant_id);

CREATE TABLE IF NOT EXISTS orders (
    order_id      BIGSERIAL PRIMARY KEY,
    tenant_id     TEXT NOT NULL REFERENCES tenants (tenant_id),
    customer_id   BIGINT NOT NULL REFERENCES customers (customer_id),
    order_date    TIMESTAMPTZ NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('completed', 'pending', 'cancelled', 'refunded')),
    total_amount  NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_orders_tenant ON orders (tenant_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders (order_date);
CREATE INDEX IF NOT EXISTS idx_orders_tenant_created ON orders (tenant_id, created_at);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id BIGSERIAL PRIMARY KEY,
    tenant_id     TEXT NOT NULL REFERENCES tenants (tenant_id),
    order_id      BIGINT NOT NULL REFERENCES orders (order_id),
    product_id    BIGINT NOT NULL REFERENCES products (product_id),
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_order_items_tenant ON order_items (tenant_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items (product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_tenant_created ON order_items (tenant_id, created_at);

CREATE TABLE IF NOT EXISTS payments (
    payment_id     BIGSERIAL PRIMARY KEY,
    tenant_id      TEXT NOT NULL REFERENCES tenants (tenant_id),
    order_id       BIGINT NOT NULL REFERENCES orders (order_id),
    amount         NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    payment_method TEXT NOT NULL,
    status         TEXT NOT NULL CHECK (status IN ('success', 'pending', 'failed', 'refunded')),
    paid_at        TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_payments_tenant ON payments (tenant_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON payments (order_id);
CREATE INDEX IF NOT EXISTS idx_payments_tenant_created ON payments (tenant_id, created_at);

CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id BIGSERIAL PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenants (tenant_id),
    customer_id     BIGINT NOT NULL REFERENCES customers (customer_id),
    plan            TEXT NOT NULL CHECK (plan IN ('basic', 'pro', 'enterprise')),
    status          TEXT NOT NULL CHECK (status IN ('active', 'cancelled')),
    mrr_amount      NUMERIC(10, 2) NOT NULL CHECK (mrr_amount >= 0),
    started_at      TIMESTAMPTZ NOT NULL,
    cancelled_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant ON subscriptions (tenant_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer ON subscriptions (customer_id);

CREATE TABLE IF NOT EXISTS events (
    event_id        UUID PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenants (tenant_id),
    customer_id     BIGINT REFERENCES customers (customer_id),
    session_id      TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    product_id      BIGINT REFERENCES products (product_id),
    event_timestamp TIMESTAMPTZ NOT NULL,
    payload         JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_events_tenant ON events (tenant_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events (event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events (event_timestamp);
CREATE INDEX IF NOT EXISTS idx_events_tenant_created ON events (tenant_id, created_at);
