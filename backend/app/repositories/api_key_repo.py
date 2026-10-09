from sqlalchemy import select
from app.models.api_key import ApiKey
from app.repositories.base import TenantScopedRepository


class ApiKeyRepository(TenantScopedRepository[ApiKey]):
    model = ApiKey

    def find_active_by_prefix(self, prefix: str) -> list[ApiKey]:
        stmt = select(ApiKey).where(ApiKey.tenant_id == self.tenant_id, ApiKey.key_prefix == prefix, ApiKey.revoked_at.is_(None))
        return list(self.db.scalars(stmt).all())
