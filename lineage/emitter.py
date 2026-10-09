"""Explicit OpenLineage event emission — adds DataPulse-specific context
(tenant, pipeline name) on top of whatever Spark's own listener captures
automatically."""
from __future__ import annotations
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from openlineage.client import OpenLineageClient
from openlineage.client.event_v2 import Dataset, Job, Run, RunEvent, RunState
from openlineage.client.uuid import generate_new_uuid
from lineage.config import load_config

logger = logging.getLogger("lineage.emitter")


def _client() -> OpenLineageClient:
    config = load_config()
    return OpenLineageClient(url=config.marquez_url)


@contextmanager
def lineage_run(job_name: str, tenant_id: str, input_datasets: list[str], output_datasets: list[str]):
    config = load_config()
    client = _client()
    run_id = str(generate_new_uuid())
    run = Run(runId=run_id)
    job = Job(namespace=config.namespace, name=job_name)

    inputs = [Dataset(namespace=config.namespace, name=name) for name in input_datasets]
    outputs = [Dataset(namespace=config.namespace, name=name) for name in output_datasets]

    start_event = RunEvent(eventType=RunState.START, eventTime=datetime.now(timezone.utc).isoformat(), run=run, job=job, producer="https://github.com/datapulse/lineage-emitter", inputs=inputs, outputs=[])
    client.emit(start_event)
    logger.info("Lineage START: job=%s run=%s tenant=%s", job_name, run_id, tenant_id)

    try:
        yield run_id
    except Exception:
        fail_event = RunEvent(eventType=RunState.FAIL, eventTime=datetime.now(timezone.utc).isoformat(), run=run, job=job, producer="https://github.com/datapulse/lineage-emitter", inputs=inputs, outputs=outputs)
        client.emit(fail_event)
        raise
    else:
        complete_event = RunEvent(eventType=RunState.COMPLETE, eventTime=datetime.now(timezone.utc).isoformat(), run=run, job=job, producer="https://github.com/datapulse/lineage-emitter", inputs=inputs, outputs=outputs)
        client.emit(complete_event)
        logger.info("Lineage COMPLETE: job=%s run=%s", job_name, run_id)
