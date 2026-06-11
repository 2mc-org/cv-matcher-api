from __future__ import annotations

from langgraph.graph.state import CompiledStateGraph

from app.graph.core.states.job_graph_state import JobGraphContext, JobGraphState

JobCompiledGraph = CompiledStateGraph[
    JobGraphState,
    JobGraphContext,
    JobGraphState,
    JobGraphState,
]
