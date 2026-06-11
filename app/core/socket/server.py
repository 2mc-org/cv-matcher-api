"""Socket.IO server initialization and access"""

import asyncio
import logging
from typing import Any

import socketio
from fastapi import FastAPI

from app.core.socket.json_encoder import PydanticJSON

logger = logging.getLogger(__name__)

# Future that will hold the Socket.IO server (like Promise in JS)
_sio_future: asyncio.Future[socketio.AsyncServer] = asyncio.Future()


def init_sio(app: FastAPI) -> socketio.AsyncServer:
    """Initialize Socket.IO server with the FastAPI app"""
    # Create Socket.IO server with custom JSON encoder for Pydantic models
    sio = socketio.AsyncServer(
        async_mode="asgi",
        cors_allowed_origins="*",
        json=PydanticJSON,  # Use custom JSON encoder
        ping_timeout=60,  # Timeout for ping/pong in seconds
        ping_interval=25,  # Interval between pings in seconds
        transports=["websocket", "polling"],  # Allow both transports
    )

    app.mount("/ws/socket.io", socketio.ASGIApp(sio, socketio_path="/"))

    # Resolve the future with the Socket.IO server
    _sio_future.set_result(sio)

    async def connect(
        sid: str, environ: dict[str, Any], auth: dict[str, Any] | None
    ) -> None:
        """Handle Socket.IO client connection"""
        try:
            if auth:
                room = auth.get("ROOM", "")
            else:
                room = environ.get("HTTP_ROOM", "")

            if room:
                await sio.enter_room(sid, room)
                logger.info("Client %s connected to room: %s", sid, room)
            else:
                logger.info("Client %s connected without room", sid)
        except Exception:
            logger.exception("Error in connect handler")
            # Don't raise exception to allow connection

    sio.on("connect", handler=connect)

    return sio


def get_sio() -> socketio.AsyncServer:
    """Get the global Socket.IO server instance"""
    if _sio_future.done():
        return _sio_future.result()
    raise RuntimeError("Socket.IO server not initialized. Call init_sio first.")


async def get_sio_async() -> socketio.AsyncServer:
    """Get the Socket.IO server asynchronously (waits if not ready)"""
    return await _sio_future
