from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

from app.core.utils.clone_field import clone_field


class UpdatedAtField(SQLModel):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # Create a new Field with sa_column for each subclass
        cls.updated_at = Field(
            default_factory=lambda: datetime.now(UTC),
            description="Last update timestamp",
            sa_column=Column(
                DateTime(timezone=True),
                onupdate=lambda: datetime.now(UTC),
            ),
        )

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UpdatedAtFieldOptional(SQLModel):
    updated_at: datetime | None = clone_field(UpdatedAtField, None)
