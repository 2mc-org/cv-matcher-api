"""Worker node: find and rank profiles (first search or changed criteria)."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from dependency_injector.wiring import Provide, inject
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.runtime import Runtime

from app.graph.core.containers.graph_services_container import (
    GraphServicesContainer,
)
from app.graph.core.states.graph_state import GraphContext, GraphState
from app.graph.cv_search_graph.services.profile_match_service import (
    ProfileMatchService,
)


@inject
async def match_profiles(
    state: GraphState,
    runtime: Runtime[GraphContext],
    profile_match_service: ProfileMatchService = Provide[
        GraphServicesContainer.profile_match_service
    ],
) -> dict[str, Any]:
    user_message = runtime.context.user_message
    result = await profile_match_service.match(state, user_message)

    return state.with_updates(
        GraphState(
            cv_search_profile_ids=list(result.ranked_profile_ids),
            cv_search_messages=[
                HumanMessage(content=user_message, id=str(uuid4())),
                AIMessage(content=result.message, id=str(uuid4())),
            ],
        ),
    )
