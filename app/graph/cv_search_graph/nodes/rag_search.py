"""Worker node: hybrid RAG search + ranking."""

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
from app.graph.cv_search_graph.services.rag_search_service import (
    RagSearchService,
)


@inject
async def rag_search(
    state: GraphState,
    runtime: Runtime[GraphContext],
    rag_search_service: RagSearchService = Provide[
        GraphServicesContainer.rag_search_service
    ],
) -> dict[str, Any]:
    user_message = runtime.context.user_message
    result = await rag_search_service.search(state, user_message)

    return state.with_updates(
        GraphState(
            cv_search_profile_ids=list(result.ranked_profile_ids),
            cv_search_messages=[
                HumanMessage(content=user_message, id=str(uuid4())),
                AIMessage(content=result.message, id=str(uuid4())),
            ],
        ),
    )
