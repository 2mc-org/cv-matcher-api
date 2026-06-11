"""CV RAG API: semantic search and proposal draft generation."""

from dependency_injector.wiring import inject
from fastapi import APIRouter

from app.core.containers.services_container import (
    CvIngestServiceDependency,
    CvSearchServiceDependency,
)
from app.cv.schemas.cv_search_hit import CvSearchProfileResult
from app.cv.schemas.cv_search_request import CvSearchRequest

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/search", response_model=list[CvSearchProfileResult])
@inject
def cv_search(
    request: CvSearchRequest,
    search_service: CvSearchServiceDependency,
) -> list[CvSearchProfileResult]:
    """Hybrid semantic search over ingested CV chunks."""
    return search_service.search(request)


@router.post("/reindex", response_model=int)
@inject
def cv_reindex(
    ingest_service: CvIngestServiceDependency,
) -> int:
    """Reindex all CV chunks."""
    return ingest_service.reindex_all()
