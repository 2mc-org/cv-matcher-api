from app.core.base_repository import BaseRepository
from app.interrupt_registry.models.base import InterruptRegistry


class InterruptRegistryRepository(BaseRepository[InterruptRegistry]):
    def __init__(self) -> None:
        super().__init__(InterruptRegistry)
