from typing import Generic, TypeVar
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class TenantScopedRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, db: Session, tenant_id: UUID) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def list(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).where(self.model.tenant_id == self.tenant_id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get(self, id_: UUID) -> ModelType | None:
        stmt = select(self.model).where(self.model.tenant_id == self.tenant_id, self.model.id == id_)
        return self.db.scalars(stmt).first()

    def create(self, **kwargs) -> ModelType:
        obj = self.model(tenant_id=self.tenant_id, **kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
