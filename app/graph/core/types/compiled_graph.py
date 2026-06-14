from __future__ import annotations

from langgraph.graph.state import CompiledStateGraph

from app.graph.core.states.graph_state import GraphContext, GraphState

CompiledGraph = CompiledStateGraph[
    GraphState,
    GraphContext,
    GraphState,
    GraphState,
]
