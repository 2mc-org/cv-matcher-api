"""Emit success response over Socket.IO."""

from __future__ import annotations

import logging
from typing import Any

from dependency_injector.wiring import Provide, inject
from langgraph.runtime import Runtime

from app.core.containers.services_container import ServicesContainer
from app.core.socket.emitter import SioEmitter
from app.graph.core.states.graph_state import GraphContext, GraphState
from app.graph.cv_search_graph.enums.cv_search_intent_route import (
    CvSearchIntentRoute,
)

logger = logging.getLogger(__name__)


@inject
async def finalize_response(
    state: GraphState,
    runtime: Runtime[GraphContext],
    sio_emitter: SioEmitter = Provide[ServicesContainer.sio_emitter],
) -> None:
    if state.cv_search_intent is None:
        msg = "cv_search_intent is required before finalize_response"
        raise ValueError(msg)

    room = runtime.context.socket_room
    action = state.cv_search_intent.action
    if action == CvSearchIntentRoute.RAG_SEARCH:
        kind = "search"
        profile_ids = list(state.cv_search_profile_ids)
    elif action == CvSearchIntentRoute.ANSWER:
        kind = "follow_up"
        profile_ids = []
    else:
        msg = f"unexpected cv_search_intent action for finalize_response: {action}"
        raise ValueError(msg)

    payload: dict[str, Any] = {
        "message": next(reversed(state.cv_search_messages)).content,
        "kind": kind,
        "profile_ids": profile_ids,
    }
    logger.info("finalize_response payload=%r", payload)
    await sio_emitter.emit_message(
        room=room,
        payload=payload,
        topic="cv_search:response",
        format="json",
    )
