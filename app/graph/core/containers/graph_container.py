from typing import Annotated

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from fastapi import Depends

from app.graph.core.types.job_compiled_graph import JobCompiledGraph


class GraphContainerBase:
    """Typed provider names for graph DI (use with cast on DependenciesContainer slot)."""

    parent_graph: providers.Provider[JobCompiledGraph | None]


class GraphContainer(GraphContainerBase, containers.DeclarativeContainer):
    """Overridden in FastAPI lifespan after the LangGraph checkpointer pool starts."""

    parent_graph = providers.Object(None)


JobGraphDependency = Annotated[
    JobCompiledGraph,
    Depends(Provide[GraphContainer.parent_graph]),
]
