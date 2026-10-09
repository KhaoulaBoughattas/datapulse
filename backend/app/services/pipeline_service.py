from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.pipeline import Pipeline
from app.repositories.data_source_repo import DataSourceRepository
from app.repositories.pipeline_repo import PipelineRepository
from app.schemas.pipeline import PipelineCreateRequest


def create_pipeline(db: Session, tenant_id: UUID, payload: PipelineCreateRequest) -> Pipeline:
    if payload.data_source_id is not None:
        data_source_repo = DataSourceRepository(db, tenant_id)
        if data_source_repo.get(payload.data_source_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="data_source_id does not exist or does not belong to your tenant")

    pipeline_repo = PipelineRepository(db, tenant_id)
    return pipeline_repo.create(
        name=payload.name,
        pipeline_type=payload.pipeline_type,
        data_source_id=payload.data_source_id,
        schedule=payload.schedule,
        is_active=True,
    )
