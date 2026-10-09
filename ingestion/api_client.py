from __future__ import annotations

import logging
from uuid import UUID
import httpx

logger = logging.getLogger("ingestion.api_client")


class DataPulseApiClient:
    def __init__(self, base_url: str, access_token: str) -> None:
        self._client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=10.0)

    def get_or_create_pipeline(self, name: str, pipeline_type: str = "BATCH") -> UUID:
        resp = self._client.get("/pipelines")
        resp.raise_for_status()
        for pipeline in resp.json():
            if pipeline["name"] == name:
                return UUID(pipeline["id"])
        create_resp = self._client.post("/pipelines", json={"name": name, "pipeline_type": pipeline_type})
        create_resp.raise_for_status()
        return UUID(create_resp.json()["id"])

    def register_dataset(self, name: str, layer: str, location: str, pipeline_id: UUID) -> UUID:
        resp = self._client.post("/datasets", json={"name": name, "layer": layer, "location": location, "pipeline_id": str(pipeline_id)})
        resp.raise_for_status()
        return UUID(resp.json()["id"])

    def start_pipeline_run(self, pipeline_id: UUID) -> UUID:
        resp = self._client.post("/pipeline-runs", json={"pipeline_id": str(pipeline_id), "status": "RUNNING", "records_processed": 0})
        resp.raise_for_status()
        return UUID(resp.json()["id"])

    def finish_pipeline_run(self, run_id: UUID, status: str, records_processed: int, error_message: str | None = None) -> None:
        resp = self._client.patch(f"/pipeline-runs/{run_id}", json={"status": status, "records_processed": records_processed, "error_message": error_message})
        resp.raise_for_status()


    def register_quality_result(self, check_name: str, passed: bool, score: float, details: dict, dataset_id=None) -> None:
        resp = self._client.post("/quality", json={"check_name": check_name, "passed": passed, "score": score, "details": details, "dataset_id": dataset_id})
        resp.raise_for_status()

    def close(self) -> None:
        self._client.close()
