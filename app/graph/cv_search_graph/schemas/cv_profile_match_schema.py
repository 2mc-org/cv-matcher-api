"""Structured output for the match_profiles sub-agent."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CvProfileMatchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        description="User-facing Markdown answer to the search request."
    )
    ranked_profile_ids: list[str] = Field(
        default_factory=list,
        description="Profile ids from cv_search tool, best first.",
    )
