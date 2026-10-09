from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_pipelines: int
    active_pipelines: int
    total_pipeline_runs: int
    successful_pipeline_runs: int
    failed_pipeline_runs: int
    pipeline_success_rate: float | None
    total_records_processed: int
    average_data_quality_score: float | None
