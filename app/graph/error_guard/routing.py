"""Shared routing: END when state.errors is non-empty, else continue."""

from __future__ import annotations

from collections.abc import Hashable
from enum import StrEnum

from langgraph.graph import END

from app.graph.core.routing.conditional_edge import (
    ConditionalEdgeRouting,
    RouteSpec,
)
from app.graph.core.states.job_graph_state import JobGraphState


class ErrorsGuardRouting(ConditionalEdgeRouting):
    """errors_guard -> END | continue_node (continue target set per subgraph)."""

    class Route(StrEnum):
        END = "errors_guard:__end__"
        CONTINUE = "errors_guard:continue"

    _SPECS = (
        RouteSpec(Route.END, END, "errors:present"),
        RouteSpec(Route.CONTINUE, "__continue__", "errors:missing"),
    )

    @classmethod
    def route(cls, state: JobGraphState) -> ErrorsGuardRouting.Route:
        if len(state.errors) > 0:
            return cls.Route.END
        return cls.Route.CONTINUE

    @classmethod
    def paths(cls, continue_node: str) -> dict[Hashable, str]:
        return {
            cls.Route.END: END,
            cls.Route.CONTINUE: continue_node,
        }
