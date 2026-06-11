from typing import Annotated, cast

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from fastapi import Depends

from app.core.containers.core_container import CoreContainer
from app.core.containers.repositories_container import RepositoriesContainer
from app.core.socket.emitter import SioEmitter
from app.graph.core.containers.graph_container import GraphContainerBase
from app.graph.core.services.graph_interrupt_service import (
    GraphInterruptService,
)
from app.graph.core.services.job_graph_diagram_service import (
    JobGraphDiagramService,
)
from app.graph.parent_graph.services.parent_graph_runner import (
    ParentGraphRunner,
)
from app.interrupt_registry.services.interrupt_registry_service import (
    InterruptRegistryService,
)


class GraphServicesContainer(containers.DeclarativeContainer):
    """DI for LangGraph node services (LLM / extraction per subgraph)."""

    wiring_config = CoreContainer.wiring_config

    graph_container = cast(
        GraphContainerBase,
        providers.DependenciesContainer(),
    )

    job_graph_diagram_service = providers.Factory(
        JobGraphDiagramService,
        graph=graph_container.parent_graph,
    )
    graph_interrupt_registry_service = providers.Factory(
        InterruptRegistryService,
        repo=RepositoriesContainer.interrupt_registry_repository,
    )
    graph_interrupt_service = providers.Factory(
        GraphInterruptService,
        sio_emitter=providers.Factory(
            SioEmitter,
            sio=CoreContainer.sio,
        ),
        interrupt_registry_service=graph_interrupt_registry_service,
    )
    parent_graph_runner = providers.Factory(
        ParentGraphRunner,
        graph=graph_container.parent_graph,
        redis=CoreContainer.redis,
        graph_interrupt_service=graph_interrupt_service,
        interrupt_registry_service=graph_interrupt_registry_service,
    )


JobGraphDiagramServiceDependency = Annotated[
    JobGraphDiagramService,
    Depends(Provide[GraphServicesContainer.job_graph_diagram_service]),
]

ParentGraphRunnerDependency = Annotated[
    ParentGraphRunner,
    Depends(Provide[GraphServicesContainer.parent_graph_runner]),
]
