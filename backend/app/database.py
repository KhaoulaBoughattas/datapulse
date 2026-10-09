"""SQLAlchemy engine and session management, with RLS session-variable
wiring: every request-scoped session sets app.current_tenant_id so
Postgres's RLS policies enforce tenant isolation as a second layer
beneath TenantScopedRepository."""
from __future__ import annotations
from collections.abc import Generator
from uuid import UUID
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_rls_tenant_context(db: Session, tenant_id: UUID) -> None:
    """SET LOCAL scopes to the current transaction only — does not leak
    to the next request reusing a pooled connection."""
    db.execute(text("SET LOCAL app.current_tenant_id = :tenant_id"), {"tenant_id": str(tenant_id)})
