from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.auth.rbac import require_permission
from app.database import get_db
from app.metrics import data_quality_score
from app.models.user import User
from app.repositories.quality_repo import QualityRepository
from app.schemas.quality import QualityResultCreateRequest, QualityResultResponse

router = APIRouter(prefix="/quality", tags=["quality"])


@router.get("", response_model=list[QualityResultResponse])
def list_quality_results(current_user: User = Depends(require_permission("quality:read")), db: Session = Depends(get_db)):
    return QualityRepository(db, current_user.tenant_id).list()


@router.post("", response_model=QualityResultResponse, status_code=status.HTTP_201_CREATED)
def create_quality_result(payload: QualityResultCreateRequest, current_user: User = Depends(require_permission("quality:write")), db: Session = Depends(get_db)):
    repo = QualityRepository(db, current_user.tenant_id)
    result = repo.create(dataset_id=payload.dataset_id, check_name=payload.check_name, passed=payload.passed, score=payload.score, details=payload.details)
    data_quality_score.labels(tenant_id=str(current_user.tenant_id), check_name=payload.check_name).set(payload.score)
    return result
