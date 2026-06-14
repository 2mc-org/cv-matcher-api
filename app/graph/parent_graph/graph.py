from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.types import Checkpointer

from app.graph.core.states.graph_state import GraphContext, GraphState
from app.graph.core.types.compiled_graph import CompiledGraph
from app.graph.core.utils.node_error_handler import node_error_handler
from app.graph.cv_search_graph.graph import compile_cv_search_graph


def compile_parent_graph(checkpointer: Checkpointer) -> CompiledGraph:
    graph = StateGraph(GraphState, context_schema=GraphContext)
    graph.add_node(
        "cv_search_graph",
        compile_cv_search_graph(),
        error_handler=node_error_handler(END),
    )

    graph.add_edge(START, "cv_search_graph")
    graph.add_edge("cv_search_graph", END)

    return graph.compile(checkpointer=checkpointer)
