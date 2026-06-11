"""Wrapper for Socket.IO handlers to set up database session context"""

from typing import Any


def wrap_handler_with_session(handler_func: Any) -> Any:
    """Wrap Socket.IO handler to set up database session context before calling"""
    from app.core.db.database import get_session, session_ctx

    async def wrapper(sid: str, data: dict[str, Any], namespace: str) -> None:
        # Create session and set context for dependency injection
        async for session in get_session():
            try:
                session_ctx.set(session)
                # Call handler - @inject decorator will handle dependency injection
                # when session_ctx is set, repositories can access it
                await handler_func(sid, data, namespace)
            finally:
                pass

    return wrapper
