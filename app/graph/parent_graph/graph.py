from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.types import Checkpointer

from app.graph.core.states.job_graph_state import JobGraphContext, JobGraphState
from app.graph.core.types.job_compiled_graph import JobCompiledGraph


def compile_parent_graph(checkpointer: Checkpointer) -> JobCompiledGraph:
    graph = StateGraph(JobGraphState, context_schema=JobGraphContext)

    graph.add_edge(START, END)

    return graph.compile(checkpointer=checkpointer)
