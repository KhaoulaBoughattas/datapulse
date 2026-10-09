"""Thin wrapper around the DataPulse API for pipeline-run lifecycle
tracking from within Airflow tasks."""
from __future__ import annotations

import os
import httpx


def _api_base_url() -> str:
    return os.getenv("DATAPULSE_API_BASE_URL", "http://backend:8000")


def get_service_token(tenant_slug: str, email: str, password: str) -> str:
    """Password-based service auth. Phase 17 replaces this with API keys —
    left as password auth here since Phase 17 isn't in this repo yet."""
    resp = httpx.post(
        f"{_api_base_url()}/auth/login",
        json={"tenant_slug": tenant_slug, "email": email, "password": password},
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_or_create_pipeline(token: str, name: str, pipeline_type: str = "BATCH") -> str:
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(base_url=_api_base_url(), headers=headers, timeout=10.0) as client:
        resp = client.get("/pipelines")
        resp.raise_for_status()
        for pipeline in resp.json():
            if pipeline["name"] == name:
                return pipeline["id"]
        create_resp = client.post("/pipelines", json={"name": name, "pipeline_type": pipeline_type})
        create_resp.raise_for_status()
        return create_resp.json()["id"]


def start_pipeline_run(token: str, pipeline_id: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(base_url=_api_base_url(), headers=headers, timeout=10.0) as client:
        resp = client.post("/pipeline-runs", json={"pipeline_id": pipeline_id, "status": "RUNNING", "records_processed": 0})
        resp.raise_for_status()
        return resp.json()["id"]


def finish_pipeline_run(token: str, run_id: str, status: str, records_processed: int, error_message: str | None = None) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(base_url=_api_base_url(), headers=headers, timeout=10.0) as client:
        resp = client.patch(
            f"/pipeline-runs/{run_id}",
            json={"status": status, "records_processed": records_processed, "error_message": error_message},
        )
        resp.raise_for_status()
