from __future__ import annotations

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.core.states.graph_state import GraphContext, GraphState
from app.graph.core.utils.node_error_handler import node_error_handler
from app.graph.cv_search_graph.nodes import CvSearchNodes
from app.graph.cv_search_graph.nodes.classify_intent import classify_intent
from app.graph.cv_search_graph.nodes.finalize_response import finalize_response
from app.graph.cv_search_graph.nodes.follow_up import follow_up
from app.graph.cv_search_graph.nodes.rag_search import rag_search
from app.graph.cv_search_graph.nodes.reject_intent import reject_intent
from app.graph.cv_search_graph.nodes.resolve_phase import resolve_phase
from app.graph.cv_search_graph.nodes.summarize_messages import (
    summarize_messages,
)
from app.graph.cv_search_graph.routing import CvSearchClassifyIntentRouting
from app.graph.error_guard.add_errors_guard import add_errors_guard


def compile_cv_search_graph() -> CompiledStateGraph[
    GraphState,
    GraphContext,
    GraphState,
    GraphState,
]:
    graph = StateGraph(GraphState, context_schema=GraphContext)

    graph.add_node(
        CvSearchNodes.RESOLVE_PHASE,
        resolve_phase,
        error_handler=node_error_handler(END),
        metadata={"description": "Derive cv_search_phase from checkpoint"},
    )
    graph.add_node(
        CvSearchNodes.SUMMARIZE_MESSAGES,
        summarize_messages,
        error_handler=node_error_handler(END),
        metadata={
            "description": "Summarize cv_search_messages when history is too long",
        },
    )
    graph.add_node(
        CvSearchNodes.CLASSIFY_INTENT,
        classify_intent,
        error_handler=node_error_handler(END),
        metadata={
            "description": "Classify user message and write cv_search_intent"
        },
    )
    graph.add_node(
        CvSearchNodes.REJECT_INTENT,
        reject_intent,
        error_handler=node_error_handler(END),
        metadata={"description": "Reject validation/off-topic intent"},
    )
    graph.add_node(
        CvSearchNodes.RAG_SEARCH,
        rag_search,
        error_handler=node_error_handler(END),
        metadata={"description": "RAG search + ranking"},
    )
    graph.add_node(
        CvSearchNodes.FOLLOW_UP,
        follow_up,
        error_handler=node_error_handler(END),
        metadata={"description": "Follow-up answer"},
    )
    graph.add_node(
        CvSearchNodes.FINALIZE_RESPONSE,
        finalize_response,
        error_handler=node_error_handler(END),
        metadata={"description": "Emit success response over Socket.IO"},
    )

    add_errors_guard(
        graph,
        continue_node=CvSearchNodes.RESOLVE_PHASE,
    )

    graph.add_edge(
        CvSearchNodes.RESOLVE_PHASE,
        CvSearchNodes.SUMMARIZE_MESSAGES,
    )
    graph.add_edge(
        CvSearchNodes.SUMMARIZE_MESSAGES,
        CvSearchNodes.CLASSIFY_INTENT,
    )

    graph.add_conditional_edges(
        CvSearchNodes.CLASSIFY_INTENT,
        CvSearchClassifyIntentRouting.route,
        CvSearchClassifyIntentRouting.PATHS,
    )
    graph.add_edge(CvSearchNodes.REJECT_INTENT, END)
    graph.add_edge(CvSearchNodes.RAG_SEARCH, CvSearchNodes.FINALIZE_RESPONSE)
    graph.add_edge(CvSearchNodes.FOLLOW_UP, CvSearchNodes.FINALIZE_RESPONSE)
    graph.add_edge(CvSearchNodes.FINALIZE_RESPONSE, END)

    return graph.compile()
