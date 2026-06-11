from typing import Any, Literal, Self

from langgraph.types import Interrupt
from pydantic import Field

from app.core.socket.events.base import SioEventBase

SioInterruptTopic = Literal["wait_job_html"]


class SioInterruptEvent(SioEventBase):
    """LangGraph interrupt value and socket ``interrupt`` event payload."""

    topic: SioInterruptTopic = Field(
        default=...,
        description="Interrupt kind; used by the client to choose a handler",
    )

    interrupt_id: str | None = Field(
        default=None,
        description=(
            "LangGraph interrupt id; set on wire, omitted in interrupt() value"
        ),
    )

    payload: str | None = Field(
        default=None, description="Body: text, dict, or list"
    )

    def to_interrupt(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_interrupt(cls, interrupt: Interrupt) -> Self:
        return cls.model_validate(interrupt.value)
