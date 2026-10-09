"""GET /lineage: tenant-scoped, RBAC-gated projection of Marquez's graph."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.auth.rbac import require_permission
from app.models.user import User
from app.schemas.lineage import LineageGraphResponse

router = APIRouter(prefix="/lineage", tags=["lineage"])


@router.get("", response_model=LineageGraphResponse)
def get_lineage(dataset: str | None = Query(default=None), current_user: User = Depends(require_permission("dataset:read"))):
    try:
        from lineage.marquez_client import get_tenant_lineage_graph
    except ImportError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Lineage module unavailable") from exc

    tenant_slug = current_user.tenant.slug
    try:
        graph = get_tenant_lineage_graph(tenant_slug, dataset_name=dataset)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Could not reach Marquez: {exc}") from exc

    return {
        "nodes": [{"id": n.id, "node_type": n.node_type, "name": n.name} for n in graph.nodes],
        "edges": [{"source_id": e.source_id, "target_id": e.target_id} for e in graph.edges],
    }
