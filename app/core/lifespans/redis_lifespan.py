"""FastAPI lifespan: close the shared Redis client on shutdown."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.core.containers.core_container import CoreContainer


@asynccontextmanager
async def redis_lifespan(
    container: CoreContainer,
) -> AsyncGenerator[None]:
    try:
        yield
    finally:
        await container.redis().aclose()
