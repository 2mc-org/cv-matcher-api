"""Reusable LangGraph ``error_handler`` factory for ``JobGraphState``."""

from __future__ import annotations

import logging
from collections.abc import Hashable, Sequence
from typing import Any, cast

from langgraph.errors import NodeError
from langgraph.graph import END
from langgraph.types import Command, Send

from app.graph.core.states.graph_state import GraphState

GotoTarget = Hashable | Send | Sequence[Send | Hashable]

logger = logging.getLogger(__name__)


def node_error_handler(
    goto: GotoTarget = END,
) -> Any:
    """Build an async error handler that records ``NodeError`` and routes to ``goto``."""

    async def handler(
        state: GraphState,
        error: NodeError,
    ) -> Command[Hashable]:
        logger.exception(
            "Graph node %s failed", error.node, exc_info=error.error
        )
        return Command(
            update=state.add_error(error),
            goto=goto,
        )

    return cast(Any, handler)
