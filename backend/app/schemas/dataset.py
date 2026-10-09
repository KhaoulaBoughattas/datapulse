from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.dataset import DatasetLayer


class DatasetCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    layer: DatasetLayer
    location: str = Field(min_length=1)
    pipeline_id: UUID | None = None


class DatasetResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    tenant_id: UUID
    name: str
    layer: DatasetLayer
    location: str
    pipeline_id: UUID | None
    created_at: datetime
