import contextvars
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session_manager import sessionmanager

session_ctx: contextvars.ContextVar[AsyncSession] = contextvars.ContextVar(
    "session_ctx"
)


async def rollback_active_session() -> None:
    """Rollback the request session after a failed SQL statement.

    Required before LangGraph node retries reuse the same FastAPI session.
    """
    try:
        session = session_ctx.get()
    except LookupError:
        return
    await session.rollback()


async def get_scoped_session() -> AsyncGenerator[AsyncSession]:
    if sessionmanager.scoped_session is None:
        raise Exception("DatabaseSessionManager is not initialized")

    # Create a new scoped session
    async with sessionmanager.scoped_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_session() -> AsyncGenerator[AsyncSession]:
    if sessionmanager.session is None:
        raise Exception("DatabaseSessionManager is not initialized")

    # Create a new session
    async with sessionmanager.session() as session:
        try:
            session_ctx.set(session)
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Create type aliases for dependency injection
DatabaseSession = Annotated[AsyncSession, Depends(get_session)]
DatabaseScopedSession = Annotated[AsyncSession, Depends(get_scoped_session)]
