"""Structured output for the follow-up sub-agent."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CvFollowUpResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(description="User-facing follow-up answer.")
