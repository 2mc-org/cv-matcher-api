"""Worker node: follow-up answer without RAG."""

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
from app.graph.cv_search_graph.services.follow_up_service import FollowUpService


@inject
async def follow_up(
    state: GraphState,
    runtime: Runtime[GraphContext],
    follow_up_service: FollowUpService = Provide[
        GraphServicesContainer.follow_up_service
    ],
) -> dict[str, Any]:
    user_message = runtime.context.user_message

    result = await follow_up_service.answer(state, user_message)

    return state.with_updates(
        GraphState(
            cv_search_messages=[
                HumanMessage(content=user_message, id=str(uuid4())),
                AIMessage(content=result.message, id=str(uuid4())),
            ],
        ),
    )
