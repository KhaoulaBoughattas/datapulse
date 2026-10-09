from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class QualityResultCreateRequest(BaseModel):
    check_name: str = Field(min_length=1, max_length=200)
    passed: bool
    score: float = Field(ge=0, le=100)
    details: dict[str, Any] | None = None
    dataset_id: UUID | None = None


class QualityResultResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    tenant_id: UUID
    dataset_id: UUID | None
    check_name: str
    passed: bool
    score: float
    details: dict[str, Any] | None
    run_at: datetime
