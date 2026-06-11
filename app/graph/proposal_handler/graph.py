from __future__ import annotations

from typing import NoReturn

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from app.graph.core.states.job_graph_state import JobGraphContext, JobGraphState


async def proposal_not_implemented(
    state: JobGraphState,
    runtime: Runtime[JobGraphContext],
) -> NoReturn:
    del state, runtime
    raise NotImplementedError("proposal_handler is not implemented yet")


def compile_proposal_handler_graph() -> CompiledStateGraph[
    JobGraphState,
    JobGraphContext,
    JobGraphState,
    JobGraphState,
]:
    graph = StateGraph(JobGraphState, context_schema=JobGraphContext)
    graph.add_node("proposal_not_implemented", proposal_not_implemented)
    graph.add_edge(START, "proposal_not_implemented")
    graph.add_edge("proposal_not_implemented", END)
    return graph.compile()
