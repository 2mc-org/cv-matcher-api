from typing import Any

from sqlmodel import Field, SQLModel

from app.core.utils.clone_field import clone_field


class InterruptRegistryTopicField(SQLModel):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        cls.topic = Field(
            ...,
            max_length=128,
            description="Socket interrupt topic",
        )

    topic: str = Field(...)


class InterruptRegistryTopicFieldOptional(SQLModel):
    topic: str | None = clone_field(InterruptRegistryTopicField, None)
