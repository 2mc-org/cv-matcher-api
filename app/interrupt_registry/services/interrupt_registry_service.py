from sqlmodel import col

from app.core.base_service import BaseService
from app.interrupt_registry.enums.status import InterruptRegistryStatus
from app.interrupt_registry.models.base import InterruptRegistry
from app.interrupt_registry.models.filters import InterruptRegistryFilters
from app.interrupt_registry.services.interrupt_registry_repository import (
    InterruptRegistryRepository,
)


class InterruptRegistryService(BaseService[InterruptRegistry]):
    """Persist and resolve LangGraph interrupt_id → thread_id mappings."""

    def __init__(self, repo: InterruptRegistryRepository) -> None:
        super().__init__(repo=repo)

    async def register(
        self,
        *,
        interrupt_id: str,
        thread_id: str,
        topic: str,
    ) -> InterruptRegistry | None:
        interrupt_registry = await self.repo.fetch_one(
            self.repo.stmt().where(
                InterruptRegistry.interrupt_id == interrupt_id
            )
        )
        if interrupt_registry:
            return interrupt_registry

        return await self.repo.add(
            InterruptRegistry(
                interrupt_id=interrupt_id, thread_id=thread_id, topic=topic
            ),
        )

    async def consume_all_pending(
        self, *, thread_id: str, exclude_interrupt_ids: list[str] | None = None
    ) -> None:
        stmt = self.repo.stmt()
        stmt = stmt.where(InterruptRegistry.thread_id == thread_id)
        stmt = stmt.where(
            InterruptRegistry.status == InterruptRegistryStatus.PENDING
        )
        if exclude_interrupt_ids:
            stmt = stmt.where(
                col(InterruptRegistry.interrupt_id).not_in(
                    exclude_interrupt_ids
                )
            )

        for row in await self.repo.fetch_many(stmt):
            row.status = InterruptRegistryStatus.CONSUMED
            await self.repo.update(row)

    async def fetch_one_with_filters_or_rise(
        self, filters: InterruptRegistryFilters
    ) -> InterruptRegistry:

        stmt = self.repo.stmt()

        populated_filters = filters.model_dump(exclude_unset=True)

        for key, value in populated_filters.items():
            stmt = stmt.where(getattr(InterruptRegistry, key) == value)

        return await self.repo.fetch_one_or_rise(stmt)
