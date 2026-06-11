"""Wire shared errors_guard node at subgraph START."""

from __future__ import annotations

from typing import Any

from langgraph.graph import START, StateGraph

from app.graph.error_guard.errors_guard import errors_guard
from app.graph.error_guard.nodes import ErrorGuardNodes
from app.graph.error_guard.routing import ErrorsGuardRouting


def add_errors_guard(
    graph: StateGraph[Any, Any, Any, Any],
    *,
    continue_node: str,
    guard_node: str = ErrorGuardNodes.ERRORS_GUARD,
    description: str = "Skip subgraph when state has errors",
) -> None:
    """START -> errors_guard -> END | continue_node."""
    graph.add_node(
        guard_node,
        errors_guard,
        metadata={"description": description},
    )
    graph.add_edge(START, guard_node)
    graph.add_conditional_edges(
        guard_node,
        ErrorsGuardRouting.route,
        ErrorsGuardRouting.paths(continue_node),
    )
