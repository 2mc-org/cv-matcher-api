"""PostgreSQL checkpointer helpers for LangGraph (psycopg / AsyncPostgresSaver)."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.graph.core.checkpoint_json_serde import GraphCheckpointJsonSerializer


async def start_postgres_checkpoint_pool(
    conn_string: str,
    *,
    run_setup: bool = True,
    min_size: int = 0,
    max_size: int = 3,
    connect_timeout: int = 10,
) -> AsyncPostgresSaver:
    """Pool-backed saver for the whole app lifetime (call :func:`stop_async_postgres_checkpoint` on shutdown).

    Avoids ``async with`` around graph usage; handlers inject the compiled graph via DI.
    Keep ``max_size`` low during local ``--reload`` to reduce fork / connection spikes with Postgres.
    """

    async def configure(conn: AsyncConnection[dict[str, Any]]) -> None:
        await conn.set_autocommit(True)
        conn.row_factory = dict_row

    pool = AsyncConnectionPool(
        conninfo=conn_string,
        kwargs={"prepare_threshold": 0, "connect_timeout": connect_timeout},
        configure=configure,
        min_size=min_size,
        max_size=max_size,
        open=False,
    )
    await pool.open()
    saver = AsyncPostgresSaver(
        pool,  # pyright: ignore[reportArgumentType]
        serde=GraphCheckpointJsonSerializer(),
    )
    if run_setup:
        await saver.setup()
    return saver


async def stop_postgres_checkpoint_pool(
    saver: AsyncPostgresSaver, *, close_timeout: float = 10.0
) -> None:
    """Close the pool or connection held by ``saver``."""
    conn = saver.conn
    if isinstance(conn, AsyncConnectionPool):
        await conn.close(timeout=close_timeout)
    elif isinstance(conn, AsyncConnection):
        await conn.close()


@asynccontextmanager
async def async_postgres_checkpointer(
    conn_string: str, *, run_setup: bool = False
) -> AsyncGenerator[AsyncPostgresSaver]:
    """Open an :class:`AsyncPostgresSaver` for the lifetime of the async context.

    Call with ``run_setup=True`` once per database (creates checkpoint tables).
    """
    async with AsyncPostgresSaver.from_conn_string(conn_string) as saver:
        if run_setup:
            await saver.setup()
        yield saver


@contextmanager
def sync_postgres_checkpointer(
    conn_string: str, *, run_setup: bool = False
) -> Generator[PostgresSaver]:
    """Sync :class:`PostgresSaver` for scripts or non-async tests."""
    with PostgresSaver.from_conn_string(conn_string) as saver:
        if run_setup:
            saver.setup()
        yield saver
