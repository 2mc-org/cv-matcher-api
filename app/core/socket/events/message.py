from typing import Any, Literal

from pydantic import Field

from app.core.socket.events.base import SioEventBase

SioMessageTopic = Literal[
    "cv_search:checkpoint",
    "cv_search:response",
    "cv_search:validation_error",
    "cv_search:off_topic_error",
]


class SioEvent(SioEventBase):
    """WebSocket event payload (``message`` event and named milestone events)."""

    topic: SioMessageTopic = Field(
        default=...,
        description="Message kind; used by the client to choose a handler",
    )

    is_error: bool = Field(
        default=False,
        description="When true, payload is an error (not a progress line)",
    )

    payload: str | dict[str, Any] | list[str] | None = Field(
        default=None, description="Body: text, dict, or list"
    )
