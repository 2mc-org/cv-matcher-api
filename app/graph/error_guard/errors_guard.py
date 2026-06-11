"""Shared LangGraph node: skip subgraph when state already has errors."""

from __future__ import annotations

from typing import Any

from app.graph.core.states.job_graph_state import JobGraphState


async def errors_guard(state: JobGraphState) -> dict[str, Any] | None:
    return None
