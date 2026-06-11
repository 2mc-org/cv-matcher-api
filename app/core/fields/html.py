from typing import Any

from sqlmodel import Field, SQLModel

from app.core.utils.clone_field import clone_field


class JobHtmlField(SQLModel):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # Create a new Field with sa_column for each subclass
        cls.html = Field(
            ...,
            min_length=1,
            max_length=1000000,
            description="Job html",
            schema_extra={"json_schema_extra": {"example": "Job html"}},
        )

    html: str = Field(
        ...,
    )


class JobHtmlFieldOptional(SQLModel):
    html: str | None = clone_field(JobHtmlField, None)
