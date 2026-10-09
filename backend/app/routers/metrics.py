"""JSON business metrics — at GET /metrics/business (not /metrics, which
is reserved for Prometheus's plain-text exposition format, mounted via
Instrumentator in main.py)."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.auth.rbac import require_permission
from app.database import get_db
from app.models.pipeline import Pipeline
from app.models.pipeline_run import PipelineRun, RunStatus
from app.models.quality import QualityResult
from app.models.user import User
from app.schemas.metrics import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/business", response_model=MetricsResponse)
def get_business_metrics(current_user: User = Depends(require_permission("pipeline:read")), db: Session = Depends(get_db)) -> MetricsResponse:
    tenant_id = current_user.tenant_id
    total_pipelines = db.scalar(select(func.count()).select_from(Pipeline).where(Pipeline.tenant_id == tenant_id)) or 0
    active_pipelines = db.scalar(select(func.count()).select_from(Pipeline).where(Pipeline.tenant_id == tenant_id, Pipeline.is_active.is_(True))) or 0
    total_runs = db.scalar(select(func.count()).select_from(PipelineRun).where(PipelineRun.tenant_id == tenant_id)) or 0
    successful_runs = db.scalar(select(func.count()).select_from(PipelineRun).where(PipelineRun.tenant_id == tenant_id, PipelineRun.status == RunStatus.SUCCESS)) or 0
    failed_runs = db.scalar(select(func.count()).select_from(PipelineRun).where(PipelineRun.tenant_id == tenant_id, PipelineRun.status == RunStatus.FAILED)) or 0
    total_records = db.scalar(select(func.coalesce(func.sum(PipelineRun.records_processed), 0)).where(PipelineRun.tenant_id == tenant_id)) or 0
    avg_quality = db.scalar(select(func.avg(QualityResult.score)).where(QualityResult.tenant_id == tenant_id))

    return MetricsResponse(
        total_pipelines=total_pipelines, active_pipelines=active_pipelines, total_pipeline_runs=total_runs,
        successful_pipeline_runs=successful_runs, failed_pipeline_runs=failed_runs,
        pipeline_success_rate=(successful_runs / total_runs) if total_runs > 0 else None,
        total_records_processed=int(total_records), average_data_quality_score=float(avg_quality) if avg_quality is not None else None,
    )
