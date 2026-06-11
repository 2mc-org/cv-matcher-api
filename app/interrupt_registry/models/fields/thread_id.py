from typing import Any

from sqlmodel import Field, SQLModel

from app.core.utils.clone_field import clone_field


class InterruptRegistryThreadIdField(SQLModel):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        cls.thread_id = Field(
            ...,
            max_length=255,
            index=True,
            description="LangGraph checkpointer thread_id",
        )

    thread_id: str = Field(...)


class InterruptRegistryThreadIdFieldOptional(SQLModel):
    thread_id: str | None = clone_field(InterruptRegistryThreadIdField, None)
