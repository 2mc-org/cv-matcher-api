from __future__ import annotations

import logging

from fastapi import BackgroundTasks
from langgraph.graph.state import RunnableConfig
from langgraph.types import Command, Interrupt
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.asyncio.lock import Lock

from app.graph.core.services.graph_interrupt_service import (
    GraphInterruptService,
)
from app.graph.core.states.job_graph_state import JobGraphContext, JobGraphState
from app.graph.core.types.job_compiled_graph import JobCompiledGraph
from app.interrupt_registry.enums.status import InterruptRegistryStatus
from app.interrupt_registry.models.filters import InterruptRegistryFilters
from app.interrupt_registry.services.interrupt_registry_service import (
    InterruptRegistryService,
)

logger = logging.getLogger(__name__)


class HandleJobPage(BaseModel):
    interrupt_id: str
    job_external_id: str
    session_hash: str


class SubmitJobPageHtml(BaseModel):
    interrupt_id: str
    html: str


class ParentGraphRunner:
    """Submit and run the parent LangGraph for one Upwork job page."""

    def __init__(
        self,
        graph: JobCompiledGraph,
        redis: Redis,
        graph_interrupt_service: GraphInterruptService,
        interrupt_registry_service: InterruptRegistryService,
    ) -> None:
        self._graph = graph
        self._redis = redis
        self._graph_interrupt_service = graph_interrupt_service
        self.interrupt_registry_service = interrupt_registry_service

    async def submit(
        self,
        data: HandleJobPage | SubmitJobPageHtml,
        background_tasks: BackgroundTasks,
    ) -> str:
        if isinstance(data, SubmitJobPageHtml):
            interrupt_registry = await self.interrupt_registry_service.fetch_one_with_filters_or_rise(
                InterruptRegistryFilters(
                    interrupt_id=data.interrupt_id,
                    status=InterruptRegistryStatus.PENDING,
                )
            )
            thread_id = interrupt_registry.thread_id
        else:
            thread_id = data.job_external_id

        lock = self._redis.lock(
            f"job_graph_run:{thread_id}",
            timeout=2 * 60 * 60,
            thread_local=False,
        )
        if not await lock.acquire(blocking=False):
            return "busy"

        background_tasks.add_task(self._run, data, lock, thread_id)
        return "end"

    async def _run(
        self,
        data: HandleJobPage | SubmitJobPageHtml,
        lock: Lock,
        thread_id: str,
    ) -> None:
        interrupts: list[Interrupt] = []
        output = JobGraphState()

        try:
            if isinstance(data, HandleJobPage):
                graph_input = JobGraphState(
                    job_external_id=data.job_external_id,
                    session_hash=data.session_hash,
                    # html=data.html,
                    errors=[],
                )
            else:
                graph_input = Command(resume={data.interrupt_id: data.html})

            context = JobGraphContext(socket_room=thread_id)
            config = RunnableConfig(
                configurable={
                    "thread_id": thread_id,
                },
            )

            async for part in self._graph.astream(
                graph_input,
                config,
                context=context,
                stream_mode=["values"],
                version="v2",
            ):
                part_type = part["type"]
                part_data = part["data"]
                part_interrupts = part.get("interrupts", ())

                if part_type == "values":
                    if isinstance(part_data, JobGraphState):
                        output = part_data
                    interrupts.extend(part_interrupts)

            if await self._graph_interrupt_service.handle_interrupts(
                room=context.socket_room,
                thread_id=thread_id,
                interrupts=interrupts,
            ):
                return

            logger.info(
                "Parent graph finished thread_id=%s job_id=%s",
                thread_id,
                output.job_id,
            )

        except Exception:
            logger.exception(
                "Parent graph failed thread_id=%s",
                thread_id,
            )
            raise
        finally:
            await lock.release()
