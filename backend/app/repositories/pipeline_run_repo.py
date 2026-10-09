from uuid import UUID
from sqlalchemy import select
from app.models.pipeline_run import PipelineRun
from app.repositories.base import TenantScopedRepository


class PipelineRunRepository(TenantScopedRepository[PipelineRun]):
    model = PipelineRun

    def list_for_pipeline(self, pipeline_id: UUID, skip: int = 0, limit: int = 100) -> list[PipelineRun]:
        stmt = (
            select(PipelineRun)
            .where(PipelineRun.tenant_id == self.tenant_id, PipelineRun.pipeline_id == pipeline_id)
            .order_by(PipelineRun.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
