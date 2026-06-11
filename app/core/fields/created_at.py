from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class CreatedAtField(SQLModel):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # Create a new Field with sa_column for each subclass
        cls.created_at = Field(
            default_factory=lambda: datetime.now(UTC),
            description="Creation timestamp",
            sa_column=Column(DateTime(timezone=True), nullable=False),
        )

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
