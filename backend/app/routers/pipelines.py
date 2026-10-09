from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.rbac import require_permission
from app.database import get_db
from app.models.user import User
from app.repositories.pipeline_repo import PipelineRepository
from app.schemas.pipeline import PipelineCreateRequest, PipelineResponse
from app.services import pipeline_service

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("", response_model=list[PipelineResponse])
def list_pipelines(current_user: User = Depends(require_permission("pipeline:read")), db: Session = Depends(get_db)):
    return PipelineRepository(db, current_user.tenant_id).list()


@router.post("", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
def create_pipeline(payload: PipelineCreateRequest, current_user: User = Depends(require_permission("pipeline:write")), db: Session = Depends(get_db)):
    return pipeline_service.create_pipeline(db, current_user.tenant_id, payload)


@router.get("/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(pipeline_id: UUID, current_user: User = Depends(require_permission("pipeline:read")), db: Session = Depends(get_db)):
    obj = PipelineRepository(db, current_user.tenant_id).get(pipeline_id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
    return obj
