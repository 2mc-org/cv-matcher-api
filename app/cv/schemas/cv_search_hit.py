"""CV semantic search API response items."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.cv.schemas.cv_chunk import CvChunkPayload


class CvSearchHit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fusion_score: float = Field(
        description="Fused hybrid search score (e.g. RRF or DBSF), not raw cosine/dot similarity.",
    )
    payload: CvChunkPayload


class CvSearchProfileResult(BaseModel):
    """One profile after aggregating multiple chunk hits."""

    model_config = ConfigDict(extra="forbid")

    profile_id: str
    full_name: str
    fusion_score: float = Field(
        description="Max fused hybrid search score across this profile's hits.",
    )
    hits: list[CvSearchHit]
