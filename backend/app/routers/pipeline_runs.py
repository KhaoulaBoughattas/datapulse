from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.auth.rbac import require_permission
from app.database import get_db
from app.metrics import pipeline_duration_seconds, pipeline_failure_total, pipeline_success_total, records_processed_total
from app.models.pipeline_run import RunStatus
from app.models.user import User
from app.repositories.pipeline_repo import PipelineRepository
from app.repositories.pipeline_run_repo import PipelineRunRepository
from app.schemas.pipeline import PipelineRunCreateRequest, PipelineRunResponse, PipelineRunUpdateRequest

router = APIRouter(prefix="/pipeline-runs", tags=["pipeline-runs"])


@router.get("", response_model=list[PipelineRunResponse])
def list_pipeline_runs(pipeline_id: UUID = Query(...), current_user: User = Depends(require_permission("pipeline:read")), db: Session = Depends(get_db)):
    return PipelineRunRepository(db, current_user.tenant_id).list_for_pipeline(pipeline_id)


@router.post("", response_model=PipelineRunResponse, status_code=status.HTTP_201_CREATED)
def create_pipeline_run(payload: PipelineRunCreateRequest, current_user: User = Depends(require_permission("pipeline:write")), db: Session = Depends(get_db)):
    repo = PipelineRunRepository(db, current_user.tenant_id)
    return repo.create(pipeline_id=payload.pipeline_id, status=payload.status, records_processed=payload.records_processed, error_message=payload.error_message)


@router.patch("/{run_id}", response_model=PipelineRunResponse)
def update_pipeline_run(run_id: UUID, payload: PipelineRunUpdateRequest, current_user: User = Depends(require_permission("pipeline:write")), db: Session = Depends(get_db)):
    run_repo = PipelineRunRepository(db, current_user.tenant_id)
    run = run_repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline run not found")

    run.status = payload.status
    run.records_processed = payload.records_processed
    run.error_message = payload.error_message
    if payload.status in (RunStatus.SUCCESS, RunStatus.FAILED):
        run.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)

    if payload.status in (RunStatus.SUCCESS, RunStatus.FAILED):
        pipeline = PipelineRepository(db, current_user.tenant_id).get(run.pipeline_id)
        pipeline_name = pipeline.name if pipeline else "unknown"
        tenant_label = str(current_user.tenant_id)

        if payload.status == RunStatus.SUCCESS:
            pipeline_success_total.labels(tenant_id=tenant_label, pipeline_name=pipeline_name).inc()
        else:
            pipeline_failure_total.labels(tenant_id=tenant_label, pipeline_name=pipeline_name).inc()

        records_processed_total.labels(tenant_id=tenant_label, pipeline_name=pipeline_name).inc(payload.records_processed)

        if run.finished_at and run.started_at:
            duration = (run.finished_at - run.started_at).total_seconds()
            pipeline_duration_seconds.labels(tenant_id=tenant_label, pipeline_name=pipeline_name).observe(duration)

    return run
