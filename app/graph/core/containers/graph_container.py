from typing import Annotated

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from fastapi import Depends

from app.graph.core.types.compiled_graph import CompiledGraph


class GraphContainerBase:
    """Typed provider names for graph DI (use with cast on DependenciesContainer slot)."""

    parent_graph: providers.Provider[CompiledGraph | None]


class GraphContainer(GraphContainerBase, containers.DeclarativeContainer):
    """Overridden in FastAPI lifespan after the LangGraph checkpointer pool starts."""

    parent_graph = providers.Object(None)


JobGraphDependency = Annotated[
    CompiledGraph,
    Depends(Provide[GraphContainer.parent_graph]),
]
