"""Socket.IO handler registration"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from app.core.socket.server import get_sio_async
from app.core.socket.session_wrapper import wrap_handler_with_session


def sio_listener(
    event: str,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """
    Decorator to register Socket.IO event handler with database session context.
    The decorator will wait for Socket.IO server to be initialized.

    Usage:
        @sio_listener("join")
        @inject
        async def handle_join(...):
            ...
    """

    def decorator(
        handler_func: Callable[..., Awaitable[Any]],
    ) -> Callable[..., Awaitable[Any]]:
        # Create async task to wait for Socket.IO server and register handler
        async def register_when_ready() -> None:
            sio = await get_sio_async()
            wrapped_handler = wrap_handler_with_session(handler_func)
            sio.on(event, handler=wrapped_handler)

        # Start the task
        asyncio.create_task(register_when_ready())

        # Return original function so it can be used with @inject
        return handler_func

    return decorator
