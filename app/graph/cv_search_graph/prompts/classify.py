"""Prompts for the classify_intent node."""

from __future__ import annotations

from app.graph.core.states.graph_state import GraphState
from app.graph.cv_search_graph.enums.cv_search_phase import CvSearchPhase


def get_classify_system_prompt() -> str:
    return """
You are the router for a CV matching assistant. You ONLY classify the user turn.
You do NOT search and you do NOT answer job questions yourself.

## Routing phase rules
Choose between answer vs rag_search:
- answer — user asks about the EXISTING shortlist without changing search
  criteria. Examples: why was candidate X picked; what skills does X have;
  compare X and Y; explain ranking; summarize a profile from the list;
  clarify previous assistant message.
- rag_search — user wants a NEW or DIFFERENT search (changed role, stack,
  seniority, location, domain, or explicit "search again" / "find others" /
  "widen/narrow criteria").
- off_topic_error — not about CV search or the current shortlist.

When unsure in follow_up phase: prefer answer if the message references
current candidates or prior results; prefer rag_search if criteria clearly
changed.
""".strip()


def get_classify_user_prompt(state: GraphState, user_message: str) -> str:
    phase = CvSearchPhase(state.cv_search_phase)
    profile_ids = (
        ", ".join(state.cv_search_profile_ids)
        if state.cv_search_profile_ids
        else "none"
    )

    return f"""
## Routing phase
{phase}

## Checkpoint snapshot
- profiles_found_count: {len(state.cv_search_profile_ids)}
- current_profile_ids: {profile_ids}

## Current user message
{user_message}
""".strip()
