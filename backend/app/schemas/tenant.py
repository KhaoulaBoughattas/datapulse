from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class TenantResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    slug: str
    name: str
    created_at: datetime
