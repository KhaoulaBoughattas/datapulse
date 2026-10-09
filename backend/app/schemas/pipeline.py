from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.pipeline import PipelineType
from app.models.pipeline_run import RunStatus


class PipelineCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    pipeline_type: PipelineType
    data_source_id: UUID | None = None
    schedule: str | None = None


class PipelineResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    tenant_id: UUID
    name: str
    pipeline_type: PipelineType
    data_source_id: UUID | None
    schedule: str | None
    is_active: bool
    created_at: datetime


class PipelineRunCreateRequest(BaseModel):
    pipeline_id: UUID
    status: RunStatus = RunStatus.RUNNING
    records_processed: int = 0
    error_message: str | None = None


class PipelineRunUpdateRequest(BaseModel):
    status: RunStatus
    records_processed: int = 0
    error_message: str | None = None


class PipelineRunResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    tenant_id: UUID
    pipeline_id: UUID
    status: RunStatus
    started_at: datetime
    finished_at: datetime | None
    records_processed: int
    error_message: str | None
