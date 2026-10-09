from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.auth.rbac import require_permission
from app.database import get_db
from app.models.user import User
from app.repositories.dataset_repo import DatasetRepository
from app.schemas.dataset import DatasetCreateRequest, DatasetResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=list[DatasetResponse])
def list_datasets(current_user: User = Depends(require_permission("dataset:read")), db: Session = Depends(get_db)):
    return DatasetRepository(db, current_user.tenant_id).list()


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(payload: DatasetCreateRequest, current_user: User = Depends(require_permission("data_source:write")), db: Session = Depends(get_db)):
    repo = DatasetRepository(db, current_user.tenant_id)
    return repo.create(name=payload.name, layer=payload.layer, location=payload.location, pipeline_id=payload.pipeline_id)
