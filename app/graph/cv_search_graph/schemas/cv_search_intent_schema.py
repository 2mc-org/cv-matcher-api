"""Orchestrator intent for one CV search turn."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.graph.cv_search_graph.enums.cv_search_intent_route import (
    CvSearchIntentRoute,
)


class CvSearchIntent(BaseModel):
    """Routing decision only — no tool calls."""

    model_config = ConfigDict(extra="forbid")

    action: CvSearchIntentRoute = Field(
        description=(
            "validation_error: when there is not enough context to form a meaningful CV search query. Write a clear message explaining what is missing in error_message."
            "off_topic_error: when the message is not about CV/job search. Write a clear message explaining what is missing in error_message."
            "match_profiles: when user wants to find or re-run CV matching."
            "follow_up: when user asks about profiles already in the shortlist."
        ),
    )
    error_message: str = Field(
        default="",
        description="User-facing text for validation_error and off_topic_error.",
    )
