from typing import Annotated

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from fastapi import Depends

from app.core.containers.core_container import CoreContainer
from app.core.containers.repositories_container import RepositoriesContainer
from app.core.socket.emitter import SioEmitter
from app.cv.services.cv_embedding_service import CvEmbeddingService
from app.cv.services.cv_ingest_service import CvIngestService
from app.cv.services.cv_qdrant_repository import CvQdrantRepository
from app.cv.services.cv_search_service import CvSearchService
from app.interrupt_registry.services.interrupt_registry_service import (
    InterruptRegistryService,
)


class ServicesContainer(containers.DeclarativeContainer):
    wiring_config = CoreContainer.wiring_config

    # Services
    interrupt_registry_service = providers.Factory(
        InterruptRegistryService,
        repo=RepositoriesContainer.interrupt_registry_repository,
    )
    sio_emitter = providers.Factory(
        SioEmitter,
        sio=CoreContainer.sio,
    )
    cv_embedding_service = providers.Singleton(CvEmbeddingService)
    cv_qdrant_repository = providers.Singleton(
        CvQdrantRepository,
        embedding_service=cv_embedding_service,
    )
    cv_ingest_service = providers.Factory(
        CvIngestService,
        embedding_service=cv_embedding_service,
        qdrant_repository=cv_qdrant_repository,
    )
    cv_search_service = providers.Factory(
        CvSearchService,
        embedding_service=cv_embedding_service,
        qdrant_repository=cv_qdrant_repository,
    )


# Services
InterruptRegistryServiceDependency = Annotated[
    InterruptRegistryService,
    Depends(Provide[ServicesContainer.interrupt_registry_service]),
]

SioEmitterDependency = Annotated[
    SioEmitter,
    Depends(Provide[ServicesContainer.sio_emitter]),
]

CvIngestServiceDependency = Annotated[
    CvIngestService,
    Depends(Provide[ServicesContainer.cv_ingest_service]),
]

CvSearchServiceDependency = Annotated[
    CvSearchService,
    Depends(Provide[ServicesContainer.cv_search_service]),
]
