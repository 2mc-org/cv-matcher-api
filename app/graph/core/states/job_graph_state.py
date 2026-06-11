"""Shared LangGraph state for parent_graph, job_page_handler, and proposal_handler."""

import traceback
from typing import Any
from uuid import UUID

from langgraph.errors import NodeError
from pydantic import BaseModel, ConfigDict, Field


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


class JobGraphContext(BaseModel):
    """Per-invoke context (``ainvoke(..., context=...)``), not checkpointed."""

    socket_room: str


class JobGraphState(BaseModel):
    """Graph state (checkpointed). Nodes return ``state.with_updates(...)``."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    errors: list[GraphNodeError] = Field(default_factory=list)

    # shared (parent routing, both handlers)
    job_external_id: str = ""
    session_hash: str = ""

    # job_page_handler
    html: str = ""
    job_id: UUID | None = None

    client_identity_id: UUID | None = None
    crm_imported_identity_hash: str | None = None

    # proposal_handler
    wants_proposal: bool = False
    cv_id: UUID | None = None

    def with_updates(self, patch: JobGraphState, /) -> dict[str, Any]:
        """Partial state update: only set fields, JSON-safe for checkpoint."""
        return patch.model_dump(mode="json", include=patch.model_fields_set)

    def add_error(self, error: NodeError, /) -> dict[str, Any]:
        """Partial state update: append one ``GraphNodeError`` from a ``NodeError``."""
        return self.with_updates(
            JobGraphState(
                errors=[*self.errors, GraphNodeError.from_node_error(error)],
            ),
        )
