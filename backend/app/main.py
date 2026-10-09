import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.routers import (
    api_keys,
    auth,
    data_sources,
    datasets,
    lineage,
    metrics,
    pipeline_runs,
    pipelines,
    quality,
    tenants,
    users,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("datapulse.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('{"event": "startup", "service": "datapulse-api"}')
    yield
    logger.info('{"event": "shutdown", "service": "datapulse-api"}')


app = FastAPI(
    title="DataPulse API",
    description="Control-plane API for the DataPulse multi-tenant data platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        '{"request_id": "%s", "method": "%s", "path": "%s", "status": %d, "duration_ms": %s}',
        request_id, request.method, request.url.path, response.status_code, duration_ms,
    )
    return response


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(api_keys.router)
app.include_router(data_sources.router)
app.include_router(pipelines.router)
app.include_router(pipeline_runs.router)
app.include_router(datasets.router)
app.include_router(quality.router)
app.include_router(metrics.router)  # exposes /metrics/business (JSON)
app.include_router(lineage.router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
