from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.rbac import require_permission
from app.database import get_db
from app.models.user import User
from app.repositories.data_source_repo import DataSourceRepository
from app.schemas.data_source import DataSourceCreateRequest, DataSourceResponse

router = APIRouter(prefix="/data-sources", tags=["data-sources"])


@router.get("", response_model=list[DataSourceResponse])
def list_data_sources(current_user: User = Depends(require_permission("data_source:read")), db: Session = Depends(get_db)) -> list:
    return DataSourceRepository(db, current_user.tenant_id).list()


@router.post("", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_data_source(payload: DataSourceCreateRequest, current_user: User = Depends(require_permission("data_source:write")), db: Session = Depends(get_db)):
    repo = DataSourceRepository(db, current_user.tenant_id)
    return repo.create(name=payload.name, source_type=payload.source_type, connection_config=payload.connection_config)


@router.get("/{data_source_id}", response_model=DataSourceResponse)
def get_data_source(data_source_id: UUID, current_user: User = Depends(require_permission("data_source:read")), db: Session = Depends(get_db)):
    obj = DataSourceRepository(db, current_user.tenant_id).get(data_source_id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found")
    return obj
