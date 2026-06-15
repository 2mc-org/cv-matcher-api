"""Routing decision after classify_intent (LangGraph conditional edges)."""

from __future__ import annotations

from app.graph.core.routing.conditional_edge import (
    ConditionalEdgeRouting,
    RouteSpec,
)
from app.graph.core.states.graph_state import GraphState
from app.graph.cv_search_graph.enums.cv_search_intent_route import (
    CvSearchIntentRoute,
)
from app.graph.cv_search_graph.nodes import CvSearchNodes


class CvSearchClassifyIntentRouting(ConditionalEdgeRouting):
    """Conditional edge after ``classify_intent``."""

    Route = CvSearchIntentRoute

    _SPECS = (
        RouteSpec(
            Route.VALIDATION_ERROR,
            CvSearchNodes.REJECT_INTENT,
            "not enough context for a CV search",
        ),
        RouteSpec(
            Route.OFF_TOPIC_ERROR,
            CvSearchNodes.REJECT_INTENT,
            "message is not about CV search",
        ),
        RouteSpec(
            Route.MATCH_PROFILES,
            CvSearchNodes.MATCH_PROFILES,
            "new search or criteria changed",
        ),
        RouteSpec(
            Route.FOLLOW_UP,
            CvSearchNodes.FOLLOW_UP,
            "question about existing shortlist",
        ),
    )

    @classmethod
    def route(cls, state: GraphState) -> CvSearchClassifyIntentRouting.Route:
        if state.cv_search_intent is None:
            msg = "cv_search_intent is required after classify_intent"
            raise ValueError(msg)
        return state.cv_search_intent.action
