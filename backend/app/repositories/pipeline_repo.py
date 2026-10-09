from app.models.pipeline import Pipeline
from app.repositories.base import TenantScopedRepository


class PipelineRepository(TenantScopedRepository[Pipeline]):
    model = Pipeline
