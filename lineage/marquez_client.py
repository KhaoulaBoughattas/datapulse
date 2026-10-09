"""Reads lineage data back OUT of Marquez, projecting it into a
simplified, tenant-scoped shape for the DataPulse API."""
from __future__ import annotations
import logging
from dataclasses import dataclass
import httpx
from lineage.config import load_config

logger = logging.getLogger("lineage.marquez_client")


@dataclass(frozen=True)
class LineageNode:
    id: str
    node_type: str
    name: str


@dataclass(frozen=True)
class LineageEdge:
    source_id: str
    target_id: str


@dataclass(frozen=True)
class LineageGraph:
    nodes: list[LineageNode]
    edges: list[LineageEdge]


def _tenant_matches(name: str, tenant_slug: str) -> bool:
    return name.endswith(f".{tenant_slug}") or f".{tenant_slug}." in name


def get_tenant_lineage_graph(tenant_slug: str, dataset_name: str | None = None) -> LineageGraph:
    config = load_config()
    nodes: dict[str, LineageNode] = {}
    edges: list[LineageEdge] = []

    with httpx.Client(base_url=config.marquez_url, timeout=10.0) as client:
        jobs_resp = client.get(f"/api/v1/namespaces/{config.namespace}/jobs")
        jobs_resp.raise_for_status()
        jobs = [j for j in jobs_resp.json().get("jobs", []) if _tenant_matches(j["name"], tenant_slug)]

        for job in jobs:
            job_id = f"job:{job['name']}"
            nodes[job_id] = LineageNode(id=job_id, node_type="job", name=job["name"])
            for ds in job.get("inputs", []):
                ds_id = f"dataset:{ds['name']}"
                nodes.setdefault(ds_id, LineageNode(id=ds_id, node_type="dataset", name=ds["name"]))
                edges.append(LineageEdge(source_id=ds_id, target_id=job_id))
            for ds in job.get("outputs", []):
                ds_id = f"dataset:{ds['name']}"
                nodes.setdefault(ds_id, LineageNode(id=ds_id, node_type="dataset", name=ds["name"]))
                edges.append(LineageEdge(source_id=job_id, target_id=ds_id))

    graph = LineageGraph(nodes=list(nodes.values()), edges=edges)

    if dataset_name:
        target_id = f"dataset:{dataset_name}"
        reachable = {target_id}
        changed = True
        while changed:
            changed = False
            for edge in edges:
                if edge.source_id in reachable and edge.target_id not in reachable:
                    reachable.add(edge.target_id)
                    changed = True
                if edge.target_id in reachable and edge.source_id not in reachable:
                    reachable.add(edge.source_id)
                    changed = True
        graph = LineageGraph(nodes=[n for n in graph.nodes if n.id in reachable], edges=[e for e in edges if e.source_id in reachable and e.target_id in reachable])

    return graph
