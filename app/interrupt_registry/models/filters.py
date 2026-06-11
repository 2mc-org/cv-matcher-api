from app.interrupt_registry.models.fields.interrupt_id import (
    InterruptRegistryInterruptIdFieldOptional,
)
from app.interrupt_registry.models.fields.status import (
    InterruptRegistryStatusFieldOptional,
)
from app.interrupt_registry.models.fields.thread_id import (
    InterruptRegistryThreadIdFieldOptional,
)
from app.interrupt_registry.models.fields.topic import (
    InterruptRegistryTopicFieldOptional,
)


class InterruptRegistryFilters(
    InterruptRegistryInterruptIdFieldOptional,
    InterruptRegistryThreadIdFieldOptional,
    InterruptRegistryTopicFieldOptional,
    InterruptRegistryStatusFieldOptional,
):
    """Filters for graph interrupt registry."""
