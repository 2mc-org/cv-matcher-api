"""Derive routing phase from checkpoint and write cv_search_phase."""

from __future__ import annotations

from typing import Any

from app.graph.core.states.graph_state import GraphState
from app.graph.cv_search_graph.enums.cv_search_phase import CvSearchPhase


async def resolve_phase(state: GraphState) -> dict[str, Any]:
    if state.cv_search_profile_ids:
        phase = CvSearchPhase.FOLLOW_UP
    else:
        phase = CvSearchPhase.SEARCH

    return state.with_updates(GraphState(cv_search_phase=phase))
