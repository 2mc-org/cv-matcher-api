from typing import Any

from sqlmodel import Field, SQLModel

from app.core.utils.clone_field import clone_field


class InterruptRegistryInterruptIdField(SQLModel):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        cls.interrupt_id = Field(
            ...,
            max_length=255,
            unique=True,
            index=True,
            description="LangGraph interrupt id",
        )

    interrupt_id: str = Field(...)


class InterruptRegistryInterruptIdFieldOptional(SQLModel):
    interrupt_id: str | None = clone_field(
        InterruptRegistryInterruptIdField, None
    )
