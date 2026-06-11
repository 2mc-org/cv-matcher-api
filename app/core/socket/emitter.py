from typing import Any

from socketio import AsyncServer

from app.core.socket.events.base import SioFormat
from app.core.socket.events.interrupt import (
    SioInterruptEvent,
    SioInterruptTopic,
)
from app.core.socket.events.message import SioEvent, SioMessageTopic


class SioEmitter:
    """Emit typed ``message`` events to Socket.IO rooms."""

    def __init__(self, sio: AsyncServer) -> None:
        self._sio = sio

    async def emit_message(
        self,
        *,
        room: str,
        payload: str | dict[str, Any] | list[str] | None = None,
        topic: SioMessageTopic,
        is_error: bool = False,
        model: str | None = None,
        format: SioFormat = "text",
    ) -> None:
        await self._sio.emit(
            "message",
            SioEvent(
                format=format,
                topic=topic,
                payload=payload,
                is_error=is_error,
                model=model,
            ),
            room=room,
        )

    async def emit_interrupt(
        self,
        *,
        room: str,
        interrupt_id: str,
        topic: SioInterruptTopic,
        payload: str | None = None,
        model: str | None = None,
        format: SioFormat = "text",
    ) -> None:
        await self._sio.emit(
            "interrupt",
            SioInterruptEvent(
                format=format,
                topic=topic,
                payload=payload,
                model=model,
                interrupt_id=interrupt_id,
            ),
            room=room,
        )
