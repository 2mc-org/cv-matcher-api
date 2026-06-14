from __future__ import annotations

from typing import NoReturn

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from app.graph.core.states.graph_state import GraphContext, GraphState


async def proposal_not_implemented(
    state: GraphState,
    runtime: Runtime[GraphContext],
) -> NoReturn:
    del state, runtime
    raise NotImplementedError("proposal_handler is not implemented yet")


def compile_proposal_handler_graph() -> CompiledStateGraph[
    GraphState,
    GraphContext,
    GraphState,
    GraphState,
]:
    graph = StateGraph(GraphState, context_schema=GraphContext)
    graph.add_node("proposal_not_implemented", proposal_not_implemented)
    graph.add_edge(START, "proposal_not_implemented")
    graph.add_edge("proposal_not_implemented", END)
    return graph.compile()
