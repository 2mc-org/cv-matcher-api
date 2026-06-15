from dependency_injector.wiring import inject
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.graph.core.containers.graph_services_container import (
    GraphDiagramServiceDependency,
)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get(
    "/diagram/cv/png",
    response_class=Response,
    responses={200: {"content": {"image/png": {}}}},
)
@inject
async def cv_graph_png(
    diagram_service: GraphDiagramServiceDependency,
    xray: int = Query(
        2,
        ge=0,
        le=10,
        description="LangGraph xray depth: 0=parent only, 1=job_page_handler nodes, 2+=inner subgraphs",
    ),
) -> Response:
    """Return PNG of the compiled parent LangGraph (debug / docs)."""
    try:
        png = diagram_service.render_parent_png(xray=xray)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return Response(content=png, media_type="image/png")
