from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.data_source import DataSourceType


class DataSourceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    source_type: DataSourceType
    connection_config: dict[str, Any] = Field(default_factory=dict)


class DataSourceResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    tenant_id: UUID
    name: str
    source_type: DataSourceType
    created_at: datetime
