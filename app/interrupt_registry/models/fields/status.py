from typing import Any

from sqlmodel import Field, SQLModel

from app.core.utils.clone_field import clone_field
from app.interrupt_registry.enums.status import InterruptRegistryStatus


class InterruptRegistryStatusField(SQLModel):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        cls.status = Field(
            default=InterruptRegistryStatus.PENDING,
            description="Interrupt resume lifecycle status",
        )

    status: InterruptRegistryStatus = Field(
        default=InterruptRegistryStatus.PENDING,
    )


class InterruptRegistryStatusFieldOptional(SQLModel):
    status: InterruptRegistryStatus | None = clone_field(
        InterruptRegistryStatusField,
        None,
    )
