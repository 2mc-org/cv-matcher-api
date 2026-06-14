"""CV semantic search API request."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.cv.enums.chunk_type import CvChunkType


class CvSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    chunk_limit: int = Field(
        default=30,
        ge=1,
        le=100,
        description="Max chunk hits to fetch from Qdrant before grouping by profile.",
    )
    chunk_types: list[CvChunkType] | None = Field(
        default=None,
        description="If omitted, search all chunk types including certificates.",
    )
    profile_id: str | None = Field(
        default=None,
        description="Restrict search to a single roster profile.",
    )
