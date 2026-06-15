from app.core.logging_config import setup_logging

setup_logging()

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.containers.core_container import CoreContainer
from app.core.containers.repositories_container import RepositoriesContainer
from app.core.containers.services_container import ServicesContainer
from app.core.custom_fast_api import CustomFastAPI
from app.core.db.session_manager import database_lifespan
from app.core.environments import environments
from app.core.lifespans.redis_lifespan import redis_lifespan
from app.core.socket.server import init_sio
from app.cv.router import router as cv_router
from app.graph.core.containers.graph_container import GraphContainer
from app.graph.core.containers.graph_services_container import (
    GraphServicesContainer,
)
from app.graph.core.lifespans.graph_checkpoint_lifespan import (
    graph_checkpoint_lifespan,
)
from app.graph.router import router as graph_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with (
        database_lifespan(app),
        graph_checkpoint_lifespan(container_graph),
        redis_lifespan(container_core),
    ):
        yield


container_core = CoreContainer()
container_repositories = RepositoriesContainer()
container_graph = GraphContainer()
container_graph_services = GraphServicesContainer(
    graph_container=container_graph,
)
container_services = ServicesContainer()


app = CustomFastAPI(
    title="CV Matcher API",
    description="Hybrid RAG search over CV profiles with agent tooling",
    version=environments.VERSION,
    debug=environments.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_sio(app)

app.state.container_core = container_core
app.state.container_repositories = container_repositories
app.state.container_graph = container_graph
app.state.container_graph_services = container_graph_services
app.state.container_services = container_services

app.include_router(cv_router)
app.include_router(graph_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": environments.SERVICE_NAME}
