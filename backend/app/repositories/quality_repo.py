from app.models.quality import QualityResult
from app.repositories.base import TenantScopedRepository


class QualityRepository(TenantScopedRepository[QualityResult]):
    model = QualityResult
