"""LangChain tool wrapping ``CvSearchService.search``."""

from __future__ import annotations

import json

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, ConfigDict, Field

from app.cv.models.cv_search_hit import CvSearchProfileResult
from app.cv.models.cv_search_request import CvSearchRequest
from app.cv.services.cv_search_service import CvSearchService


class CvSearchToolInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        description="Natural-language search query derived from the job requirements.",
    )
    chunk_limit: int = Field(
        default=30,
        description=(
            "Max chunk hits to fetch from Qdrant before grouping by profile "
            "(typically 1–100)."
        ),
    )
    profile_id: str | None = Field(
        default=None,
        description="Optional roster profile id to restrict search to one CV.",
    )


def _format_results(results: list[CvSearchProfileResult]) -> str:
    simplified = [
        {
            "profile_id": result.profile_id,
            "full_name": result.full_name,
            "fusion_score": result.fusion_score,
            "top_chunks": [
                {
                    "chunk_type": hit.payload.chunk_type,
                    "text": hit.payload.text,
                    "score": hit.fusion_score,
                }
                for hit in result.hits[:3]
            ],
        }
        for result in results[:10]
    ]
    return json.dumps(simplified, ensure_ascii=False)


def build_cv_search_tool(search_service: CvSearchService) -> StructuredTool:
    """Build the cv_search tool bound to a DI-managed search service."""

    def cv_search(
        query: str,
        chunk_limit: int = 30,
        profile_id: str | None = None,
    ) -> str:
        request = CvSearchRequest(
            query=query,
            chunk_limit=chunk_limit,
            profile_id=profile_id,
        )
        results = search_service.search(request)
        return _format_results(results)

    return StructuredTool.from_function(
        func=cv_search,
        name="cv_search",
        description=(
            "Hybrid semantic search over ingested CV profiles. "
            "Returns ranked profiles with relevance scores and top matching chunks."
        ),
        args_schema=CvSearchToolInput,
    )
