"""FastAPI lifespan: Postgres checkpointer pool + compiled parent graph."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dependency_injector import providers

from app.core.environments import environments
from app.graph.core.checkpointer import (
    start_postgres_checkpoint_pool,
    stop_postgres_checkpoint_pool,
)
from app.graph.core.containers.graph_container import GraphContainer
from app.graph.parent_graph.graph import compile_parent_graph


@asynccontextmanager
async def graph_checkpoint_lifespan(
    graph_container: GraphContainer,
) -> AsyncGenerator[None]:
    dsn = environments.get_checkpointer_db_url()
    saver = await start_postgres_checkpoint_pool(
        dsn,
        run_setup=True,
        min_size=environments.POSTGRES_CHECKPOINTER_POOL_MIN_SIZE,
        max_size=environments.POSTGRES_CHECKPOINTER_POOL_MAX_SIZE,
    )

    parent_graph = compile_parent_graph(saver)
    graph_container.parent_graph.override(providers.Object(parent_graph))

    try:
        yield
    finally:
        graph_container.parent_graph.reset_override()
        await stop_postgres_checkpoint_pool(saver)
