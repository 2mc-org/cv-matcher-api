"""Shared LangGraph state for parent_graph and cv_search_graph."""

import traceback
from typing import Annotated, Any

from langchain_core.messages import AnyMessage
from langgraph.errors import NodeError
from langgraph.graph.message import add_messages
from langmem.short_term import RunningSummary
from pydantic import BaseModel, ConfigDict, Field

from app.graph.cv_search_graph.enums.cv_search_phase import CvSearchPhase
from app.graph.cv_search_graph.schemas.cv_search_intent_schema import (
    CvSearchIntent,
)


class GraphNodeError(BaseModel):
    """One failed node captured by a LangGraph ``error_handler``."""

    model_config = ConfigDict(extra="forbid")

    node: str
    type: str
    message: str
    traceback: str | None = None

    @classmethod
    def from_node_error(cls, error: NodeError) -> GraphNodeError:
        exc = error.error
        return cls(
            node=error.node,
            type=type(exc).__name__,
            message=str(exc),
            traceback="".join(
                traceback.TracebackException.from_exception(exc).format()
            )
            or None,
        )


class GraphContext(BaseModel):
    """Per-invoke context (``ainvoke(..., context=...)``), not checkpointed."""

    socket_room: str
    user_message: str = ""


class GraphState(BaseModel):
    """Graph state (checkpointed). Nodes return partial updates."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    errors: list[GraphNodeError] = Field(default_factory=list)

    cv_search_profile_ids: list[str] = Field(default_factory=list)
    cv_search_phase: CvSearchPhase | None = None
    cv_search_intent: CvSearchIntent | None = None

    # cv search chat history and summarized messages
    cv_search_messages: Annotated[list[AnyMessage], add_messages] = Field(
        default_factory=list,
    )
    cv_search_summarized_messages: list[AnyMessage] = Field(
        default_factory=list
    )
    cv_search_running_summary: RunningSummary | None = None

    @classmethod
    def with_updates(cls, patch: GraphState, /) -> dict[str, Any]:
        """Partial state update: only set fields, JSON-safe for checkpoint."""
        return patch.model_dump(mode="json", include=patch.model_fields_set)

    def add_error(self, error: NodeError, /) -> dict[str, Any]:
        """Partial state update: append one ``GraphNodeError`` from a ``NodeError``."""
        return self.with_updates(
            GraphState(
                errors=[*self.errors, GraphNodeError.from_node_error(error)],
            ),
        )
