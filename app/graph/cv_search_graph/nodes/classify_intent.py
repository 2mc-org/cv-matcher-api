"""Classify user turn intent and write cv_search_intent to state."""

from __future__ import annotations

from typing import Any

from dependency_injector.wiring import Provide, inject
from langgraph.runtime import Runtime

from app.core.containers.services_container import ServicesContainer
from app.core.socket.emitter import SioEmitter
from app.graph.core.containers.graph_services_container import (
    GraphServicesContainer,
)
from app.graph.core.states.graph_state import GraphContext, GraphState
from app.graph.cv_search_graph.services.classify_intent_service import (
    ClassifyIntentService,
)


@inject
async def classify_intent(
    state: GraphState,
    runtime: Runtime[GraphContext],
    classify_intent_service: ClassifyIntentService = Provide[
        GraphServicesContainer.classify_intent_service
    ],
    sio_emitter: SioEmitter = Provide[ServicesContainer.sio_emitter],
) -> dict[str, Any]:
    room = runtime.context.socket_room
    user_message = runtime.context.user_message

    await sio_emitter.emit_message(
        room=room,
        payload="Analyzing message...",
        topic="cv_search:checkpoint",
    )

    intent = await classify_intent_service.classify(state, user_message)

    return state.with_updates(GraphState(cv_search_intent=intent))
