CREATE TABLE IF NOT EXISTS ingestion_watermarks (
    tenant_id      TEXT NOT NULL,
    table_name     TEXT NOT NULL,
    last_extracted_at TIMESTAMPTZ NOT NULL,
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, table_name)
);
