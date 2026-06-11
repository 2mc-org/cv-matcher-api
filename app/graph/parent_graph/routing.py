"""Parent graph routing: job_page_handler then proposal_handler."""

from __future__ import annotations

from enum import StrEnum

from app.graph.core.states.job_graph_state import JobGraphState


class ParentRoutePath(StrEnum):
    JOB_PAGE_HANDLER = "job_page_handler"
    PROPOSAL_HANDLER = "proposal_handler"
    END = "__end__"


def route_parent(state: JobGraphState) -> ParentRoutePath:
    if state.job_id is None:
        return ParentRoutePath.JOB_PAGE_HANDLER
    if state.wants_proposal:
        return ParentRoutePath.PROPOSAL_HANDLER
    return ParentRoutePath.END
