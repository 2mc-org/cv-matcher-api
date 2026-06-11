"""Global LangGraph interrupt handling: notify clients and resume runs."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from langgraph.types import Interrupt

from app.core.socket.emitter import SioEmitter
from app.core.socket.events.interrupt import SioInterruptEvent
from app.interrupt_registry.services.interrupt_registry_service import (
    InterruptRegistryService,
)

logger = logging.getLogger(__name__)


class GraphInterruptService:
    """Notify clients about pending graph interrupts."""

    def __init__(
        self,
        sio_emitter: SioEmitter,
        interrupt_registry_service: InterruptRegistryService,
    ) -> None:
        self.sio_emitter = sio_emitter
        self.interrupt_registry_service = interrupt_registry_service

    async def handle_interrupts(
        self,
        *,
        room: str,
        thread_id: str,
        interrupts: Sequence[Interrupt],
    ) -> bool:
        """Emit pending interrupts to the client. Returns True when paused."""
        await self.interrupt_registry_service.consume_all_pending(
            thread_id=thread_id,
            exclude_interrupt_ids=[interrupt.id for interrupt in interrupts],
        )

        if not interrupts:
            return False

        for interrupt in interrupts:
            value = SioInterruptEvent.from_interrupt(interrupt)

            await self.interrupt_registry_service.register(
                interrupt_id=interrupt.id,
                thread_id=thread_id,
                topic=value.topic,
            )

            await self.sio_emitter.emit_interrupt(
                room=room,
                interrupt_id=interrupt.id,
                topic=value.topic,
                format=value.format,
                model=value.model,
                payload=value.payload,
            )

        return True
