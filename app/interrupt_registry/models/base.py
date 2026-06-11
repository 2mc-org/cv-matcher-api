from typing import Any, ClassVar

from sqlmodel import SQLModel

from app.core.fields.base_fields import BaseFields
from app.interrupt_registry.models.fields.interrupt_id import (
    InterruptRegistryInterruptIdField,
)
from app.interrupt_registry.models.fields.status import (
    InterruptRegistryStatusField,
)
from app.interrupt_registry.models.fields.thread_id import (
    InterruptRegistryThreadIdField,
)
from app.interrupt_registry.models.fields.topic import (
    InterruptRegistryTopicField,
)


class InterruptRegistry(
    BaseFields,
    InterruptRegistryInterruptIdField,
    InterruptRegistryThreadIdField,
    InterruptRegistryTopicField,
    InterruptRegistryStatusField,
    SQLModel,
    table=True,
):
    """Maps LangGraph interrupt_id to checkpointer thread_id for resume."""

    __tablename__: ClassVar[Any] = "interrupt_registry"

    class Config:
        from_attributes = True
