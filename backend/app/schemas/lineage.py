from pydantic import BaseModel


class LineageNodeResponse(BaseModel):
    id: str
    node_type: str
    name: str


class LineageEdgeResponse(BaseModel):
    source_id: str
    target_id: str


class LineageGraphResponse(BaseModel):
    nodes: list[LineageNodeResponse]
    edges: list[LineageEdgeResponse]
