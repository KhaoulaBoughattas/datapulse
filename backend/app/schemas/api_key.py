from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ApiKeyCreateResponse(BaseModel):
    id: UUID
    name: str
    raw_key: str
    key_prefix: str
    created_at: datetime


class ApiKeyResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    tenant_id: UUID
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None
