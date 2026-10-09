from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.tenant import Tenant


class TenantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_slug(self, slug: str) -> Tenant | None:
        return self.db.scalars(select(Tenant).where(Tenant.slug == slug)).first()

    def get(self, tenant_id: UUID) -> Tenant | None:
        return self.db.get(Tenant, tenant_id)

    def create(self, slug: str, name: str) -> Tenant:
        tenant = Tenant(slug=slug, name=name)
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant
