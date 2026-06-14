"""CV RAG API: semantic search and proposal draft generation."""

from dependency_injector.wiring import inject
from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.containers.services_container import (
    CvIngestServiceDependency,
    CvSearchServiceDependency,
)
from app.core.db.database import DatabaseSession
from app.cv.models.actions.search_cv_data import SearchCvData
from app.cv.models.cv_search_hit import CvSearchProfileResult
from app.cv.models.cv_search_request import CvSearchRequest
from app.graph.core.containers.graph_services_container import (
    ParentGraphRunnerDependency,
)

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/search", response_model=list[CvSearchProfileResult])
@inject
def cv_search(
    request: CvSearchRequest,
    search_service: CvSearchServiceDependency,
) -> list[CvSearchProfileResult]:
    """Hybrid semantic search over ingested CV chunks."""
    return search_service.search(request)


@router.post("/search/agent", response_model=str)
@inject
async def cv_search_agent(
    request: SearchCvData,
    parent_graph_runner: ParentGraphRunnerDependency,
    background_tasks: BackgroundTasks,
    session: DatabaseSession,
) -> str:
    """Run CV search agent graph for one thread (``end`` or ``busy``)."""
    try:
        return await parent_graph_runner.submit(request, background_tasks)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}") from e


@router.post("/reindex", response_model=int)
@inject
def cv_reindex(
    ingest_service: CvIngestServiceDependency,
) -> int:
    """Reindex all CV chunks."""
    return ingest_service.reindex_all()
