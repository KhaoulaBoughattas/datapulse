export type Role = 'OWNER' | 'ADMIN' | 'DATA_ENGINEER' | 'ANALYST' | 'VIEWER';

export interface CurrentUser {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
}

export interface Pipeline {
  id: string;
  tenant_id: string;
  name: string;
  pipeline_type: 'BATCH' | 'STREAMING';
  data_source_id: string | null;
  schedule: string | null;
  is_active: boolean;
  created_at: string;
}

export interface PipelineRun {
  id: string;
  tenant_id: string;
  pipeline_id: string;
  status: 'RUNNING' | 'SUCCESS' | 'FAILED';
  started_at: string;
  finished_at: string | null;
  records_processed: number;
  error_message: string | null;
}

export interface DataSource {
  id: string;
  tenant_id: string;
  name: string;
  source_type: 'POSTGRES' | 'REST_API' | 'KAFKA';
  created_at: string;
}

export interface Dataset {
  id: string;
  tenant_id: string;
  name: string;
  layer: 'BRONZE' | 'SILVER' | 'GOLD';
  location: string;
  pipeline_id: string | null;
  created_at: string;
}

export interface QualityResult {
  id: string;
  tenant_id: string;
  dataset_id: string | null;
  check_name: string;
  passed: boolean;
  score: number;
  details: Record<string, unknown> | null;
  run_at: string;
}

export interface BusinessMetrics {
  total_pipelines: number;
  active_pipelines: number;
  total_pipeline_runs: number;
  successful_pipeline_runs: number;
  failed_pipeline_runs: number;
  pipeline_success_rate: number | null;
  total_records_processed: number;
  average_data_quality_score: number | null;
}

export interface LineageNode {
  id: string;
  node_type: 'dataset' | 'job';
  name: string;
}
export interface LineageEdge {
  source_id: string;
  target_id: string;
}
export interface LineageGraph {
  nodes: LineageNode[];
  edges: LineageEdge[];
}
