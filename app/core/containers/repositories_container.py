from typing import Annotated

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from fastapi import Depends

from app.core.containers.core_container import CoreContainer
from app.interrupt_registry.services.interrupt_registry_repository import (
    InterruptRegistryRepository,
)


class RepositoriesContainer(containers.DeclarativeContainer):
    wiring_config = CoreContainer.wiring_config

    # Repositories
    interrupt_registry_repository = providers.Factory(
        InterruptRegistryRepository,
    )


# Repositories
InterruptRegistryRepositoryDependency = Annotated[
    InterruptRegistryRepository,
    Depends(Provide[RepositoriesContainer.interrupt_registry_repository]),
]
