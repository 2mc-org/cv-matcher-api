"""Emit validation/off-topic intent rejection over Socket.IO."""

from __future__ import annotations

import logging

from dependency_injector.wiring import Provide, inject
from langgraph.runtime import Runtime

from app.core.containers.services_container import ServicesContainer
from app.core.socket.emitter import SioEmitter
from app.core.socket.events.message import SioMessageTopic
from app.graph.core.states.graph_state import GraphContext, GraphState
from app.graph.cv_search_graph.enums.cv_search_intent_route import (
    CvSearchIntentRoute,
)

_ERROR_TOPICS: dict[CvSearchIntentRoute, SioMessageTopic] = {
    CvSearchIntentRoute.VALIDATION_ERROR: "cv_search:validation_error",
    CvSearchIntentRoute.OFF_TOPIC_ERROR: "cv_search:off_topic_error",
}

logger = logging.getLogger(__name__)


@inject
async def reject_intent(
    state: GraphState,
    runtime: Runtime[GraphContext],
    sio_emitter: SioEmitter = Provide[ServicesContainer.sio_emitter],
) -> None:
    if state.cv_search_intent is None:
        msg = "cv_search_intent is required for reject_intent"
        raise ValueError(msg)

    room = runtime.context.socket_room
    topic = _ERROR_TOPICS[state.cv_search_intent.action]

    logger.info(
        "reject_intent topic=%s payload=%r",
        topic,
        state.cv_search_intent.error_message,
    )
    await sio_emitter.emit_message(
        room=room,
        payload=state.cv_search_intent.error_message,
        topic=topic,
        is_error=True,
    )
