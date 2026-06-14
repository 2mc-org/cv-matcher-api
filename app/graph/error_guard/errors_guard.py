"""Shared LangGraph node: skip subgraph when state already has errors."""

from __future__ import annotations

from typing import Any

from app.graph.core.states.graph_state import GraphState


async def errors_guard(state: GraphState) -> dict[str, Any] | None:
    return None
