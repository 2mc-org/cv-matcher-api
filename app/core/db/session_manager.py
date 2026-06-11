import logging
from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from app.core.environments import environments

logger = logging.getLogger(__name__)


class DatabaseSessionManager:
    def __init__(self) -> None:
        self.database_url = environments.get_db_url(async_driver=True)
        self.engine: AsyncEngine | None = None
        self.session: async_sessionmaker[AsyncSession] | None = None
        self.scoped_session: async_scoped_session[AsyncSession] | None = None

    def init_db(self) -> None:
        # Creating an asynchronous engine
        self.engine = create_async_engine(
            self.database_url,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
        )

        # Creating an asynchronous session class
        self.session = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False,
        )

        # Creating a scoped session with asyncio.current_task as scopefunc
        self.scoped_session = async_scoped_session(
            self.session, scopefunc=current_task
        )

    async def close(self) -> None:
        # Closing the database session...
        if self.engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self.engine.dispose()


# Initialize the DatabaseSessionManager
sessionmanager = DatabaseSessionManager()


@asynccontextmanager
async def database_lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Database lifespan context manager for FastAPI application."""
    # Startup
    logger.info("Initializing database...")
    sessionmanager.init_db()

    yield

    # Shutdown
    logger.info("Closing database connections...")
    await sessionmanager.close()
